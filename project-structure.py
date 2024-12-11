import os

def print_directory_structure(startpath, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'venv', 'env'}
        
    for root, dirs, files in os.walk(startpath):
        # Excluir directorios no deseados
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f'{indent}├── {os.path.basename(root)}')
        subindent = '│   ' * (level + 1)
        
        for f in files:
            if not f.startswith('.'):
                print(f'{subindent}├── {f}')

def main():
    project_path = os.path.dirname(os.path.abspath(__file__))
    print("\nEstructura del Proyecto de Ajedrez:")
    print_directory_structure(project_path)

if __name__ == "__main__":
    main()
