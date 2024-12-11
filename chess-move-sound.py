import wave
import struct
import numpy as np
import os

def create_move_sound():
    """Crea un sonido de movimiento de pieza de ajedrez"""
    # Configuración del archivo de audio
    sample_rate = 44100  # Hz
    duration = 0.15  # segundos
    
    # Crear carpeta de recursos si no existe
    os.makedirs('gui/resources/sounds', exist_ok=True)
    
    # Generar sonido de "golpe" suave
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Frecuencia base y armónicos
    f1, f2 = 220.0, 440.0  # Frecuencias fundamentales
    
    # Generar forma de onda
    attack = 0.01
    decay = 0.14
    
    # Envolvente
    envelope = np.where(t < attack, t/attack, 
                       np.exp(-(t-attack)/(decay/5)))
    
    # Generar sonido
    wave1 = np.sin(2 * np.pi * f1 * t) * envelope
    wave2 = np.sin(2 * np.pi * f2 * t) * envelope * 0.5
    
    waveform = (wave1 + wave2) * 0.5
    
    # Normalizar
    waveform = waveform * 32767
    
    # Convertir a enteros de 16 bits
    waveform = waveform.astype(np.int16)
    
    # Crear archivo WAV
    with wave.open('gui/resources/sounds/move.wav', 'w') as wav_file:
        # Configurar parámetros
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes por muestra
        wav_file.setframerate(sample_rate)
        
        # Escribir datos
        wav_file.writeframes(waveform.tobytes())
    
    print("Archivo de sonido creado en gui/resources/sounds/move.wav")

if __name__ == '__main__':
    create_move_sound()
