import sqlite3

conn = sqlite3.connect("livros.db")

conn.execute("""
INSERT INTO livros (titulo, autor, categoria, pdf)
VALUES (
    'Harry Potter',
    'J.K Rowling',
    'Fantasia',
    'harry_potter_todos_os_capitulos.pdf'
)
""")

print("Livro adicionado!")

conn.execute("""
INSERT INTO livros (titulo, autor, categoria, pdf)
VALUES (
    'Memorial de Aires',
    'Machado de Assis',
    'Romance',
    'memoria de aires.pdf'
)
""")

conn.commit()
conn.close()

print("Livro adicionado!")

conn.execute("""
INSERT INTO livros (titulo, autor, categoria, pdf)
VALUES (
    'A mão e a Luva',
    'Machado de Assis',
    'Romance',
    'maoLuva.pdf'
)
""")

conn.commit()
conn.close()

print("Livro adicionado!")