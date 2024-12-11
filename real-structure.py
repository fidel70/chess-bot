import os

def show_tree(directory, prefix=''):
    """Muestra el árbol completo de archivos y directorios"""
    # Obtener contenido del directorio
    files = []
    dirs = []
    
    try:
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                files.append(name)
            else:
                dirs.append(name)
    except PermissionError:
        return

    # Imprimir archivos
    for i, name in enumerate(dirs):
        last = (i == len(dirs) - 1 and len(files) == 0)
        print(f"{prefix}{'└──' if last else '├──'} {name}")
        path = os.path.join(directory, name)
        extension = '    ' if last else '│   '
        show_tree(path, prefix + extension)
        
    for i, name in enumerate(files):
        last = (i == len(files) - 1)
        print(f"{prefix}{'└──' if last else '├──'} {name}")

print("\nEstructura completa del proyecto:\n")
show_tree(".")
