from paho.mqtt.client import Client
from threading import Thread

class Barra:
    """Una nueva clase que determinará la barra que usaremos para salvar la Bola, tiene 4 atributos que son el lienzo, la posición, el estado y la velocidad"""
    """Además uno llamado barra para pintar un rectángulo de cierto tamaño en una posición dada en cuanto creamos un objeto de esta clase"""
    """Por último otro atributo que nos servirá de enlace con las teclas del teclado para poder controlar los objetos de esta clase"""
   
    def __init__(self, c, posicionx, estado, speed, espectador):
        """En la init de la clase barra definiremos la posición de la barra, la velocidad de la bola y el topic al que se 
        suscriben el jugador y los espectadores para recibir comandos y proyectar la partida. 
        Si el usuario que se suscribe al topic es espectador solo podrá recibir comandos y visualizarlos en su pantalla, ejecutando un hilo con la función rec(recibir).
        En cambio si es el jugador, podrá controlar la partida con el teclado, pudiendo empezar la partida a través del hilo empezar_client.
        """
        self.posicionx = posicionx
        self.estado = estado
        self.c = c
        self.speed = speed
        self.topic = "paralelaparty_rlad"
        self.barra = self.c.create_rectangle(posicionx, 466, posicionx + 80, 476, fill = 'black')
        self.client = None
        if espectador:
            Thread(target = self.rec).start()
        else:
            self.c.bind_all("<KeyPress>", self.mover)
            Thread(target = self.empezar_client).start()
            
    def empezar_client(self):
        """Esta función conecta el cliente al broker para eviar los comandos.
        """
        self.client = Client()
        self.client.connect("broker.hivemq.com")
        self.client.loop_forever()
            
    def rec(self):
        """Esta función conecta a los espectadores al juego rompeLadrillos. 
        El espectador se suscribe al topic definido en la init y recibe los comandos a través de la función on_message
        """
        self.client = Client()
        self.client.on_message = self.on_message
        self.client.connect("broker.hivemq.com")
        self.client.subscribe(self.topic)
        self.client.loop_forever()
 
    def on_message(self, client, userdata, msg):
        """Función que recibe los comandos que le reenvía el broker. 
        Si el comando es 0, moverá a la izquierda la barra del espectador y si recibe un 1, lo moverá a la derecha
        """
        if msg.payload.decode('ascii') == '0':
            print("izq")
            self.left_espectador()
        else:
            print("der")
            self.right_espectador()
    
    def left_espectador(self):
        """Función usada para mover un objeto de la clase Barra un número de posiciones, que vienen determinados por la velocidad,"""
        """a la izquierda cada vez que se ejecute esta función, también varía de igual manera la posición de la Barra"""
        if self.posicionx > 17 and self.speed < 17:
            self.c.move(self.barra, -self.speed, 0)
            self.posicionx = self.posicionx - self.speed

    def right_espectador(self):
        """Misma función que la anterior pero sirve para el desplazamiento hacia la derecha de la Barra"""
        if self.posicionx < 689:
            self.c.move(self.barra, self.speed, 0)
            self.posicionx = self.posicionx + self.speed

    def left(self):
        """Función usada para mover un objeto de la clase Barra un número de posiciones, que vienen determinados por la velocidad,"""
        """a la izquierda cada vez que se ejecute esta función, también varía de igual manera la posición de la Barra"""
        if self.posicionx > 17 and self.speed < 17:
            self.c.move(self.barra, -self.speed, 0)
            self.posicionx = self.posicionx - self.speed
            self.client.publish(self.topic, 0)
    
    def right(self):
        """Misma función que la anterior pero sirve para el desplazamiento hacia la derecha de la Barra"""
        if self.posicionx < 689:
            self.c.move(self.barra, self.speed, 0)
            self.posicionx = self.posicionx + self.speed
            self.client.publish(self.topic, 1)
    
    
    def mover(self, evento):
        """ Relaciona la dos funciones anteriores con las teclas de dirección del teclado right y left"""
        if evento.keysym == 'Left':
            self.left()
        if evento.keysym == 'Right':
            self.right()
    
    """Función auxiliar para llevar un atributo a otra clase o fuera de ella"""
    
    def posicion(self):
        return self.posicionx


class Bloque:
    """Última clase, tiene 4 atributos que son el lienzo, 2 posiciones y un estado"""
    """Además de un atributo bloque que diburá un rectángulo de color gris del tamaño indicado en la posición proporcionado por los atributos"""
    """Esta clase no tiene funciones dentro de la misma"""
    def __init__(self, c, posx, posy, estad):
        self.posx = posx
        self.posy = posy
        self.c = c
        self.estad = estad
        self.bloque = self.c.create_rectangle(posx, posy, posx + 56, posy + 34, fill = 'grey')
            