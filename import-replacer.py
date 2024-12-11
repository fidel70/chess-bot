import re

def replace_imports():
    # Nuevas importaciones
    new_imports = '''import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
import chess

# Configurar path del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importaciones del motor
from engine.search.evaluator.material import MaterialEvaluator
from engine.search.minimax import MinimaxEngine
from engine.search.zobrist_hash import ZobristHash'''

    # Leer archivo
    with open('run-gui.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Patrón para encontrar las importaciones actuales
    pattern = r'''from engine\.evaluator\.material.*?from engine\.search\.zobrist_hash import ZobristHash'''
    
    # Reemplazar importaciones
    new_content = re.sub(pattern, new_imports, content, flags=re.DOTALL)
    
    # Guardar cambios
    with open('run-gui.py', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == "__main__":
    replace_imports()
    print("Importaciones reemplazadas exitosamente.")
