# Proyecto de Motor de Ajedrez con GUI
## Progreso Actual

### 1. Estructura del Proyecto
```
chess_engine/
├── gui/
│   ├── __init__.py
│   ├── components/
│   ├── resources/
│   │   └── pieces/      # Imágenes SVG de las piezas
│   └── main_window.py
├── engine/
│   ├── evaluator/
│   ├── search/
│   └── utils/
├── tests/
└── docs/
```

### 2. Componentes Implementados

#### GUI
- **ChessPiece**: Widget para piezas de ajedrez usando SVG
  - Tamaño: 25x25 píxeles
  - Carga dinámica de imágenes SVG

- **ChessSquare**: Casillas del tablero
  - Tamaño: 30x30 píxeles
  - Colores alternados: #F0D9B5 (claro) y #B58863 (oscuro)

- **ChessBoard**: Tablero completo
  - Matriz 8x8 de ChessSquares
  - Integración con python-chess
  - Posición inicial estándar

- **MoveList**: Panel de movimientos
  - Lista de jugadas
  - Botones de navegación (<<, <, >, >>)

- **EngineControls**: Panel de control del motor
  - Selector de profundidad (1-20)
  - Botón de análisis
  - Panel de información

- **MainWindow**: Ventana principal
  - Tamaño: 1000x600 píxeles
  - Menú con opciones básicas
  - Barra de estado

### 3. Características Implementadas
- Tablero visual completo
- Visualización correcta de piezas
- Menú básico
- Panel de control del motor
- Lista de movimientos

### 4. Próximos Pasos

#### Inmediatos
1. Implementar drag & drop de piezas
2. Validar movimientos legales
3. Conectar con el motor de ajedrez

#### Futuros
1. Implementar guardar/cargar PGN
2. Añadir análisis del motor
3. Mejorar interfaz visual
4. Añadir sonidos
5. Implementar reloj de ajedrez

### 5. Motor de Ajedrez (Fase 1 - Python Puro)
- Evaluación material básica
- Algoritmo minimax con poda alfa-beta
- Objetivo: ~2000 ELO

### 6. Dependencias
```python
chess>=1.9.0       # Lógica del juego
PyQt5>=5.15.0      # GUI
numpy>=1.21.0      # Operaciones numéricas
pytest>=7.0.0      # Testing
```

### 7. Notas Técnicas
- GUI implementada con PyQt5
- Piezas SVG estilo "merida"
- Integración con python-chess para reglas
- Estructura modular para fácil expansión

### 8. Bugs Conocidos
- Ninguno reportado hasta ahora

### 9. Mejoras Pendientes
- Optimizar tamaño del tablero
- Mejorar respuesta visual al seleccionar piezas
- Añadir indicadores de movimientos legales
