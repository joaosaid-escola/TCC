from pathlib import Path
import sqlite3


PASTA_PDFS = Path("pdfs")
PASTA_CAPAS = Path("static/capas")

conn = sqlite3.connect("livros.db")
livros = conn.execute("SELECT id, pdf, capa FROM livros").fetchall()

# Remove registros que apontam para arquivos que não existem mais.
ids_invalidos = [
    livro[0]
    for livro in livros
    if not livro[1]
    or not livro[2]
    or not (PASTA_PDFS / livro[1]).is_file()
    or not (PASTA_CAPAS / livro[2]).is_file()
]

conn.executemany("DELETE FROM livros WHERE id = ?", [(id_livro,) for id_livro in ids_invalidos])

# O PDF identifica a obra. Mantém o registro mais antigo de cada PDF.
conn.execute("""
    DELETE FROM livros
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM livros
        GROUP BY pdf
    )
""")
removidos = conn.total_changes

conn.commit()
conn.close()

print(f"Limpeza concluída: {removidos} registro(s) removido(s).")
