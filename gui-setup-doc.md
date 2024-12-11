# Configuración de GUI para Motor de Ajedrez con PyQt5

## Estructura del Proyecto

La estructura base del proyecto es:
```
chess_engine/
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── chess_board.py
│   └── components/
│       ├── __init__.py
│       └── square.py
├── docs/
├── engine/
├── tests/
├── requirements.txt
├── main.py
├── run-gui.py
└── README.md
```

## Componentes Principales

### 1. square.py
Este archivo define la clase Square que representa cada casilla del tablero.

```python
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

class Square(QWidget):
    def __init__(self, is_white=True, parent=None):
        super().__init__(parent)
        self.is_white = is_white
        self.initUI()
    
    def initUI(self):
        self.setMinimumSize(50, 50)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor('#F0D9B5') if self.is_white else QColor('#B58863')
        painter.fillRect(event.rect(), color)
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        return self.minimumSize()
```

### 2. chess_board.py
Define el tablero de ajedrez que contiene las 64 casillas.

```python
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt, QSize
from .components.square import Square

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Crear el tablero 8x8
        for row in range(8):
            for col in range(8):
                square = Square(is_white=(row + col) % 2 == 0)
                self.layout.addWidget(square, row, col)
    
    def minimumSizeHint(self):
        return QSize(400, 400)
```

### 3. main_window.py
Define la ventana principal de la aplicación.

```python
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from .chess_board import ChessBoard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Chess Engine GUI")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Tablero de ajedrez
        self.chess_board = ChessBoard()
        layout.addWidget(self.chess_board)
```

### 4. run_gui.py
Script principal para ejecutar la aplicación.

```python
import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

## Dependencias
El proyecto requiere las siguientes dependencias en requirements.txt:
```
chess>=1.9.0
numpy>=1.21.0
pytest>=7.0.0
PyQt5>=5.15.0
PyQt5-Qt5>=5.15.0
PyQt5-sip>=12.8.0
```

## Ejecución
Para ejecutar la aplicación:
1. Asegurarse de estar en el directorio raíz del proyecto (chess_engine)
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `python run-gui.py`

## Características GUI
- Tablero de ajedrez 8x8
- Casillas alternadas en colores claros (#F0D9B5) y oscuros (#B58863)
- Tamaño mínimo de ventana: 800x600 píxeles
- Tamaño mínimo de casillas: 50x50 píxeles
- Tamaño mínimo del tablero: 400x400 píxeles
