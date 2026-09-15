from flask import Flask, render_template, request, send_from_directory
import sqlite3

app = Flask(__name__)

def conectar():
    conn = sqlite3.connect("livros.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def inicio():
    busca = request.args.get("q", "").strip()
    conn = conectar()
    if busca:
        termo = f"%{busca}%"
        livros = conn.execute(
            """
            SELECT * FROM livros
            WHERE titulo LIKE ? COLLATE NOCASE
               OR autor LIKE ? COLLATE NOCASE
               OR categoria LIKE ? COLLATE NOCASE
            ORDER BY titulo
            """,
            (termo, termo, termo),
        ).fetchall()
    else:
        livros = conn.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    conn.close()

    return render_template("index.html", livros=livros, busca=busca)

@app.route('/pdfs/<nome_pdf>')
def abrir_pdf(nome_pdf):
    return send_from_directory('pdfs', nome_pdf)

if __name__ == "__main__":
    app.run(debug=True)
    
