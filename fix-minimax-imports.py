def fix_minimax_imports():
    file_path = 'engine/search/minimax.py'
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Reemplazar la importación incorrecta
    content = content.replace(
        'from engine.evaluator.material import MaterialEvaluator',
        'from engine.search.evaluator.material import MaterialEvaluator'
    )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print("Importaciones corregidas en minimax.py")

if __name__ == "__main__":
    fix_minimax_imports()
