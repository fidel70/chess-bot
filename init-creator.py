import os

def create_init_files():
    init_paths = [
        'engine/__init__.py',
        'engine/search/__init__.py',
        'engine/search/evaluator/__init__.py'
    ]
    
    for path in init_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write('')
    
    print("Archivos __init__.py creados.")

if __name__ == "__main__":
    create_init_files()
