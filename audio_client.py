# encoding: utf-8
from threading import Thread
import pyaudio

class audio():
    def __init__(self, conn):
        self.conn = conn
        print("Estableciendo parámetros...")
        # Parámetros audio
        self.tam_bloque = 1024
        self.formato_audio = pyaudio.paInt16 
        self.freq = 20000
        self.canales = 1
        
        print("Inicializando dispositivos de audio...")
        self.p = pyaudio.PyAudio()
        self.reproductor = self.p.open(format=self.formato_audio, channels=self.canales, rate=self.freq, output=True, frames_per_buffer=self.tam_bloque) 
        self.grabadora = self.p.open(format=self.formato_audio, channels=self.canales, rate=self.freq, input=True, frames_per_buffer=self.tam_bloque) 
        print("Dispositivos de audio iniciados.")
        Thread(target=self.enviar_audio).start() #Iniciamos el hilo para enviar el audio, desde cada cliente
        self.recibir_audio()
    
    def recibir_audio(self):
        print("Esperando audio...")
        while True:
            data = self.conn.recv_bytes(2048) #Siempre manda 2048 bytes, por lo que no necesitamos enviar la longitud de bytes como en el caso de la imagen
            self.reproductor.write(data) #Reproduce el audio a cada uno de los clientes

    def enviar_audio(self):
        print("Enviando audio...")
        while True:
            data = self.grabadora.read(1024, False)
            self.conn.send_bytes(data) #graba el audio de cada clientes
