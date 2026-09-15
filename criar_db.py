import sqlite3
 
conn = sqlite3.connect("livros.db")
 
conn.execute("""
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    autor TEXT,
    categoria TEXT,
    pdf TEXT,
    capa TEXT
)
""")

conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_livros_pdf ON livros(pdf)")
 
conn.execute("""
INSERT OR IGNORE INTO livros (titulo, autor, categoria, pdf, capa)
VALUES (
    'Dom Casmurro',
    'Machado de Assis',
    'Literatura',
    'dom_casmurro.pdf',
    'dom_casmurro.jpg'
)
""")

conn.execute("""
UPDATE livros
SET titulo = 'Memorial de Aires', autor = 'Machado de Assis', categoria = 'Romance',
    capa = 'Memorial de Aires.jpg'
WHERE pdf = 'memorial-de-aires.pdf'
""")
 
conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("livros.db")

conn.execute("""
INSERT OR IGNORE INTO livros (titulo, autor, categoria, pdf, capa)
VALUES (
    'Harry Potter',
    'J.K Rowling',
    'Fantasia',
    'harry_potter_todos_os_capitulos.pdf',
    'harry_potter_todos_os_capitulos.jpg'
)
""")

conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("livros.db")

conn.execute("""
INSERT OR IGNORE INTO livros (titulo, autor, categoria, pdf, capa)
VALUES (
    'Memorial de Aires',
    'Machado de Assis',
    'Romance',
    'memorial-de-aires.pdf',
    'Memorial de Aires.jpg'
)
""")
 
conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("livros.db")


conn.execute("""
INSERT OR IGNORE INTO livros (titulo, autor, categoria, pdf, capa)
VALUES (
    'O-Senhor-dos-Anéis-Vol-1',
    'J. R. R. Tolkien',
    'Fantasia',
    'O-Senhor-dos-Anéis-Vol-1.pdf',
    'O-Senhor-dos-Anéis-Vol-1.jpg'
)
""")

conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect("livros.db")

conn.execute("""
INSERT OR IGNORE INTO livros (titulo, autor, categoria, pdf, capa)
VALUES (
    'Um_sopro_de_Vida',
    'Clarice Lispector',
    'Romance',
    'Um_sopro_de_Vida.pdf',
    'Um_sopro_de_Vida.jpg'
)
""")

conn.commit()
conn.close()

print("Livro adicionado!")
