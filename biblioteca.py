import hmac
import os
import secrets
import sqlite3
from pathlib import Path

from flask import (
    Flask, abort, flash, redirect, render_template, request, send_from_directory,
    session, url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
PASTA_PDFS = BASE_DIR / "pdfs"
PASTA_CAPAS = BASE_DIR / "static" / "capas"
EXTENSOES_CAPA = {"jpg", "jpeg", "png", "webp"}


def conectar():
    conn = sqlite3.connect(BASE_DIR / "livros.db")
    conn.row_factory = sqlite3.Row
    return conn


def administrador_logado():
    return session.get("administrador") is True


def exigir_administrador():
    if not administrador_logado():
        return redirect(url_for("login", proxima=url_for("admin")))
    return None


def validar_csrf():
    token = request.form.get("csrf_token", "")
    if not hmac.compare_digest(token, session.get("csrf_token", "")):
        abort(400, description="Formulário expirado. Atualize a página e tente novamente.")


@app.before_request
def preparar_csrf():
    session.setdefault("csrf_token", secrets.token_urlsafe(32))


@app.route("/")
def inicio():
    busca = request.args.get("q", "").strip()
    conn = conectar()
    if busca:
        termo = f"%{busca}%"
        livros = conn.execute(
            """SELECT * FROM livros
               WHERE titulo LIKE ? COLLATE NOCASE
                  OR autor LIKE ? COLLATE NOCASE
                  OR categoria LIKE ? COLLATE NOCASE
               ORDER BY titulo""",
            (termo, termo, termo),
        ).fetchall()
    else:
        livros = conn.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    conn.close()
    return render_template(
        "index.html", livros=livros, busca=busca,
        administrador_logado=administrador_logado(), csrf_token=session["csrf_token"],
    )


@app.route("/pdfs/<path:nome_pdf>")
def abrir_pdf(nome_pdf):
    return send_from_directory(PASTA_PDFS, nome_pdf)


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if administrador_logado():
        return redirect(url_for("admin"))
    if request.method == "POST":
        validar_csrf()
        usuario_configurado = os.environ.get("ADMIN_USERNAME")
        senha_configurada = os.environ.get("ADMIN_PASSWORD")
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")
        if (usuario_configurado and senha_configurada
                and hmac.compare_digest(usuario, usuario_configurado)
                and hmac.compare_digest(senha, senha_configurada)):
            session.clear()
            session["administrador"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)
            flash("Login realizado.", "sucesso")
            return redirect(url_for("admin"))
        flash("Credenciais inválidas ou administrador não configurado.", "erro")
    return render_template("login.html", csrf_token=session["csrf_token"])


@app.route("/admin/logout", methods=["POST"])
def logout():
    validar_csrf()
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    acesso = exigir_administrador()
    if acesso:
        return acesso
    if request.method == "POST":
        validar_csrf()
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        categoria = request.form.get("categoria", "").strip()
        arquivo_pdf = request.files.get("pdf")
        arquivo_capa = request.files.get("capa")
        if not all((titulo, autor, categoria)) or not arquivo_pdf or not arquivo_pdf.filename:
            flash("Preencha título, autor, categoria e selecione um PDF.", "erro")
        else:
            nome_pdf = secure_filename(arquivo_pdf.filename)
            nome_capa = None
            ext_pdf = Path(nome_pdf).suffix.lower()
            if ext_pdf != ".pdf":
                flash("O arquivo do livro precisa estar no formato PDF.", "erro")
            elif arquivo_capa and arquivo_capa.filename:
                nome_capa = secure_filename(arquivo_capa.filename)
                ext_capa = Path(nome_capa).suffix.lower().lstrip(".")
                if ext_capa not in EXTENSOES_CAPA:
                    flash("A capa precisa ser JPG, PNG ou WebP.", "erro")
                    nome_capa = None
            capa_valida = not (arquivo_capa and arquivo_capa.filename) or bool(nome_capa)
            if ext_pdf == ".pdf" and capa_valida:
                PASTA_PDFS.mkdir(parents=True, exist_ok=True)
                PASTA_CAPAS.mkdir(parents=True, exist_ok=True)
                if (PASTA_PDFS / nome_pdf).exists() or (nome_capa and (PASTA_CAPAS / nome_capa).exists()):
                    flash("Já existe um arquivo com esse nome. Renomeie o arquivo antes de enviar.", "erro")
                else:
                    arquivo_pdf.save(PASTA_PDFS / nome_pdf)
                    if arquivo_capa and arquivo_capa.filename and nome_capa:
                        arquivo_capa.save(PASTA_CAPAS / nome_capa)
                    conn = conectar()
                    try:
                        conn.execute(
                            "INSERT INTO livros (titulo, autor, categoria, pdf, capa) VALUES (?, ?, ?, ?, ?)",
                            (titulo, autor, categoria, nome_pdf, nome_capa),
                        )
                        conn.commit()
                    except sqlite3.IntegrityError:
                        (PASTA_PDFS / nome_pdf).unlink(missing_ok=True)
                        if nome_capa:
                            (PASTA_CAPAS / nome_capa).unlink(missing_ok=True)
                        flash("Esse livro já está cadastrado.", "erro")
                    else:
                        flash("Livro adicionado à biblioteca.", "sucesso")
                    finally:
                        conn.close()
                    return redirect(url_for("admin"))

    conn = conectar()
    livros = conn.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    conn.close()
    return render_template("admin.html", livros=livros, csrf_token=session["csrf_token"])


@app.route("/admin/livros/<int:id_livro>/remover", methods=["POST"])
def remover_livro(id_livro):
    acesso = exigir_administrador()
    if acesso:
        return acesso
    validar_csrf()
    conn = conectar()
    livro = conn.execute("SELECT pdf, capa FROM livros WHERE id = ?", (id_livro,)).fetchone()
    if livro:
        conn.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
        conn.commit()
        for pasta, nome in ((PASTA_PDFS, livro["pdf"]), (PASTA_CAPAS, livro["capa"])):
            if nome:
                caminho = (pasta / nome).resolve()
                if caminho.parent == pasta.resolve():
                    caminho.unlink(missing_ok=True)
        flash("Livro removido.", "sucesso")
    conn.close()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
