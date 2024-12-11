import numpy as np
from scipy.io import wavfile

def generate_chess_move_sound(filename='move.wav', duration=0.15):
    """
    Genera un sonido suave y profesional para movimientos de ajedrez
    """
    # Configuración del sonido
    sample_rate = 44100  # Frecuencia de muestreo estándar
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Frecuencias para un sonido agradable
    f1, f2 = 1000, 1500  # Frecuencias base
    
    # Generamos dos ondas y las combinamos
    wave1 = np.sin(2 * np.pi * f1 * t) * 0.5
    wave2 = np.sin(2 * np.pi * f2 * t) * 0.3
    
    # Envolvente para suavizar el inicio y final
    envelope = np.ones_like(t)
    attack = int(0.01 * sample_rate)  # 10ms de attack
    release = int(0.05 * sample_rate)  # 50ms de release
    
    # Aplicar fade in
    envelope[:attack] = np.linspace(0, 1, attack)
    # Aplicar fade out
    envelope[-release:] = np.linspace(1, 0, release)
    
    # Combinar ondas y aplicar envolvente
    wave = (wave1 + wave2) * envelope
    
    # Normalizar a int16 (-32768 a 32767)
    wave = np.int16(wave * 32767)
    
    # Guardar el archivo
    wavfile.write(filename, sample_rate, wave)
    
if __name__ == '__main__':
    # Generar el sonido
    generate_chess_move_sound('move.wav')
    print("Archivo de sonido generado con éxito!")
    
    # Reproducir el sonido para prueba
    try:
        import pygame
        pygame.mixer.init()
        sound = pygame.mixer.Sound('move.wav')
        sound.play()
        pygame.time.wait(int(0.15 * 1000))  # Esperar a que termine
    except ImportError:
        print("Instala pygame para reproducir el sonido de prueba")
