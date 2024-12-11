# Documentación del Motor de Ajedrez con GUI en Python

## Estructura del Proyecto
```
chess_engine/
├── gui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── square.py         # Clase para las casillas del tablero
│   ├── resources/
│   │   └── pieces/
│   │       ├── wK.svg        # Rey blanco
│   │       ├── wQ.svg        # Dama blanca
│   │       ├── wB.svg        # Alfil blanco
│   │       ├── wN.svg        # Caballo blanco
│   │       ├── wR.svg        # Torre blanca
│   │       ├── wP.svg        # Peón blanco
│   │       ├── bK.svg        # Rey negro
│   │       ├── bQ.svg        # Dama negra
│   │       ├── bB.svg        # Alfil negro
│   │       ├── bN.svg        # Caballo negro
│   │       ├── bR.svg        # Torre negra
│   │       └── bP.svg        # Peón negro
│   ├── chess_board.py        # Clase principal del tablero
│   └── main_window.py        # Ventana principal de la aplicación
├── engine/                   # Módulo del motor de ajedrez
├── tests/                    # Directorio para pruebas
├── requirements.txt          # Dependencias del proyecto
├── setup-gui.py             # Script de configuración inicial
└── run-gui.py               # Script principal para ejecutar la GUI
```

## Componentes Principales

### 1. Square (gui/components/square.py)
- Representa una casilla individual del tablero
- Características:
  - Color alternado (marrón claro #F0D9B5 y marrón oscuro #B58863)
  - Tamaño mínimo de 50x50 píxeles
  - Capacidad para contener una pieza de ajedrez
  - Layout vertical para centrar las piezas

### 2. ChessPiece (gui/components/square.py)
- Representa una pieza de ajedrez
- Características:
  - Renderiza imágenes SVG de las piezas
  - Tamaño estándar de 45x45 píxeles
  - Sistema de mapeo entre piezas y archivos SVG

### 3. ChessBoard (gui/chess_board.py)
- Implementa el tablero completo de ajedrez
- Características:
  - Matriz 8x8 de objetos Square
  - Integración con python-chess para la lógica del juego
  - Sistema de coordenadas invertido para mostrar blancas abajo
  - Tamaño mínimo de 400x400 píxeles

### 4. MainWindow (run-gui.py)
- Ventana principal de la aplicación
- Características:
  - Tamaño mínimo de 800x600 píxeles
  - Layout vertical centrado
  - Título "Chess Engine GUI"

## Dependencias
```
chess>=1.9.0       # Librería python-chess para lógica del juego
numpy>=1.21.0      # Soporte para operaciones numéricas
pytest>=7.0.0      # Framework de pruebas
PyQt5>=5.15.0      # Framework GUI
PyQt5-Qt5>=5.15.0  # Componentes Qt
PyQt5-sip>=12.8.0  # Bindings SIP para PyQt
```

## Características Implementadas
1. Interfaz Gráfica:
   - Tablero de ajedrez 8x8 con colores alternados
   - Piezas SVG del estilo "merida"
   - Posición inicial correcta de todas las piezas
   - Ventana redimensionable con tamaños mínimos

2. Integración con python-chess:
   - Estado del tablero sincronizado con python-chess
   - Posición inicial FEN estándar
   - Base para implementar movimientos legales

## Scripts de Utilidad

### setup-gui.py
- Crea la estructura de directorios
- Descarga las piezas SVG
- Configura archivos iniciales
- Actualiza requirements.txt

### run-gui.py
- Punto de entrada de la aplicación
- Inicializa la ventana principal
- Configura el tablero
- Maneja el bucle principal de eventos

## Uso
1. Configuración inicial:
```bash
python setup-gui.py
pip install -r requirements.txt
```

2. Ejecución:
```bash
python run-gui.py
```

## Próximos Pasos Planificados
1. Implementar drag & drop para mover piezas
2. Añadir panel de información del motor
3. Crear historial de movimientos
4. Implementar controles del motor
5. Agregar barra de menú
6. Integrar el motor de análisis

## Notas Técnicas
- Los colores del tablero siguen el esquema estándar de lichess.org
- Las piezas SVG son del conjunto "merida", ampliamente usado en interfaces de ajedrez
- La estructura modular permite fácil extensión y mantenimiento
- La integración con python-chess proporciona una base sólida para la lógica del juego
