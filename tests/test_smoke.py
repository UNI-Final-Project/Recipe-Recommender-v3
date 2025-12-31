"""Test de humo: comprueba que `app.py` existe y que su sintaxis es válida."""
import ast
import os


def test_app_syntax():
    path = os.path.join(os.getcwd(), 'app.py')
    assert os.path.exists(path), 'No se encontró app.py en la raíz del repo'
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    # Parsear el AST para detectar errores de sintaxis sin ejecutar el fichero
    ast.parse(src)
    assert True
