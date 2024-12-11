import chess
import time
import sys
import psutil
import numpy as np
from motor.search.evaluator.material import MaterialEvaluator
from minimaxengine import MinimaxEngine  # Tu versión anterior
#from minimax_engine_optimized import MinimaxEngine as MinimaxEngineOptimized  # Nueva versión

def get_memory_usage():
    """Retorna el uso de memoria en MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def test_position(fen: str, depth: int, engine, name: str):
    """Prueba una posición específica y retorna métricas."""
    board = chess.Board(fen)
    
    start_memory = get_memory_usage()
    start_time = time.time()
    
    best_move, evaluation = engine.search(board, time_limit=30)  # 30 segundos máximo
    
    end_time = time.time()
    end_memory = get_memory_usage()
    
    time_spent = end_time - start_time
    memory_used = end_memory - start_memory
    nodes_per_second = engine.search_info.nodes_searched / time_spent if time_spent > 0 else 0
    
    print(f"\nResultados para {name}:")
    print(f"Posición: {fen}")
    print(f"Mejor jugada encontrada: {best_move}")
    print(f"Evaluación: {evaluation:.2f}")
    print(f"Tiempo: {time_spent:.2f} segundos")
    print(f"Nodos explorados: {engine.search_info.nodes_searched}")
    print(f"Nodos por segundo: {nodes_per_second:.0f}")
    print(f"Memoria utilizada: {memory_used:.2f} MB")
    print(f"Profundidad alcanzada: {engine.search_info.depth_reached}")
    
    return {
        'time': time_spent,
        'nodes': engine.search_info.nodes_searched,
        'memory': memory_used,
        'nps': nodes_per_second,
        'move': best_move,
        'eval': evaluation
    }

def main():
    # Posiciones de prueba
    test_positions = [
        # Posición inicial
        "rnbqkbnr/pppp1ppp/8/4p3/3N4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
        
    ]
    
    # Profundidad de búsqueda
    depth = 3
    
    # Inicializar motores
    evaluator = MaterialEvaluator()
    original_engine = MinimaxEngine(evaluator, depth=depth)
    #optimized_engine = MinimaxEngineOptimized(evaluator, depth=depth)
    
    results = {'original': [], 'optimized': []}
    
    print("Iniciando pruebas comparativas...")
    
    for pos in test_positions:
        print("\n" + "="*50)
        print(f"Probando posición:\n{chess.Board(pos)}")
        
        # Probar motor original
        results['original'].append(
            test_position(pos, depth, original_engine, "Motor Original")
        )
        
        # # Probar motor optimizado
        # results['optimized'].append(
        #     test_position(pos, depth, optimized_engine, "Motor Optimizado")
        # )
        
    # Mostrar resumen comparativo
    print("\n" + "="*50)
    print("\nResumen comparativo:")
    print("\nPromedios:")
    for engine_type in ['original', 'optimized']:
        avg_time = np.mean([r['time'] for r in results[engine_type]])
        avg_nodes = np.mean([r['nodes'] for r in results[engine_type]])
        avg_memory = np.mean([r['memory'] for r in results[engine_type]])
        avg_nps = np.mean([r['nps'] for r in results[engine_type]])
        
        print(f"\n{engine_type.title()}:")
        print(f"Tiempo promedio: {avg_time:.2f} segundos")
        print(f"Nodos promedio: {avg_nodes:.0f}")
        print(f"Memoria promedio: {avg_memory:.2f} MB")
        print(f"Nodos por segundo: {avg_nps:.0f}")

if __name__ == "__main__":
    main()
