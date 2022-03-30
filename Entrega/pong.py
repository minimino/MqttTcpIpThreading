import turtle
from threading import Thread
from multiprocessing import Queue
from queue import Empty

class Pong():
    def __init__(self, conn, id, mi_nombre, nombre_oponente):
        self.id = id
        self.conn = conn
        # El ID del contrincante será 1 si el de este jugador es 0 y 0 si este jugador es 1
        self.id_contr = 1 - id
        self.cola = Queue()
        
        # Establecemos los nombres de los jugadores
        if id == 0:
            self.jugador1 = mi_nombre
            self.jugador2 = nombre_oponente
        else:
            self.jugador1 = nombre_oponente
            self.jugador2 = mi_nombre
            
        # Creamos pantalla con el fondo negro            
        self.pantalla = turtle.Screen()
        self.pantalla.title("Tenis multijugador")
        self.pantalla.bgcolor("black")
        self.pantalla.setup(600, 400)
        self.pantalla.tracer(0)
        
        # Puntos iniciales de cada jugador        
        self.puntos1 = 0
        self.puntos2 = 0

        # Objetos
        # Raqueta 1
        self.raqueta1 = turtle.Turtle()
        self.raqueta1.penup()
        self.raqueta1.color("white")    # Color blanco de la raqueta
        self.raqueta1.speed(0)          # Velocidad movimiento raqueta
        self.raqueta1.shape("square")   # Forma de la raqueta
        self.raqueta1.shapesize(3,0.75)
        self.raqueta1.goto(-270, 0)

        # Raqueta 2
        self.raqueta2 = turtle.Turtle()
        self.raqueta2.penup()
        self.raqueta2.color("white")    # Color blanco de la raqueta
        self.raqueta2.speed(0)          # Velocidad movimiento raqueta
        self.raqueta2.shape("square")   # Forma de la raqueta
        self.raqueta2.shapesize(3,0.75)
        self.raqueta2.goto(270, 0)
        
        # Bola
        self.bola = turtle.Turtle()
        self.bola.penup()
        self.bola.color("white")   # Color blanco de la bola
        self.raqueta2.speed(0)     # Velocidad movimiento raqueta
        self.bola.shape("circle")  # Forma de la bola
        self.bola.shapesize(0.5,0.5)
        self.start_bola()

        # Marcador de puntuación
        self.marcador = turtle.Turtle()
        self.marcador.hideturtle()
        self.marcador.penup()
        self.marcador.color("white")   # Color blanco del marcador
        self.marcador.goto(0, 165)
        self.marcador.write(self.jugador1 + ": " + str(self.puntos1) + " " + self.jugador2 + ": " + str(self.puntos2), align="center", font=("Arial", 15, "bold")) # Texto marcador

        self.pantalla.listen()

        # Botones para ejecutar los movimientos de las raquetas
        self.pantalla.onkeypress(self.raqueta_arriba, "Up")
        self.pantalla.onkeypress(self.raqueta_abajo, "Down")
        
        # Recibimos comandos del oponente
        Thread(target=self.recibir_raqueta).start()

        # Movimientos de la bola
        while True:
            self.pantalla.update()             
            self.bola.setx(self.bola.xcor() + self.bola.velx)
            self.bola.sety(self.bola.ycor() + self.bola.vely)
           
            try:
                # Vemos si hay algún comando en la cola y si no, pasamos
                com = int.from_bytes(self.cola.get(False), byteorder='big')
                print(com)
                if com == 0:
                    self.raqueta_arriba_Contr()
                elif com == 1:
                    self.raqueta_abajo_Contr()
                
            except Empty:
                pass
           
            if self.bola.ycor() > 200: # La bola ha llegado al techo
                self.bola.sety(200)
                self.bola.vely *= -1
            elif self.bola.ycor() < -200: # La bola ha llegado al suelo
                self.bola.sety(-200)
                self.bola.vely *= -1
           
            if self.bola.xcor() > 300:
                self.bola.goto(0,0)
                self.bola.velx = -0.1
                self.puntos1 += 1
                self.marcador.clear()
                self.marcador.write(self.jugador1 + ": " + str(self.puntos1) + " " + self.jugador2 + ": " + str(self.puntos2), align="center", font=("Arial", 15, "bold"))
            elif self.bola.xcor() < -300: # La bola ha llegado al lado izquierdo
                self.bola.goto(0,0)
                self.bola.velx = 0.1
                self.puntos2 += 1
                self.marcador.clear()
                self.marcador.write(self.jugador1 + ": " + str(self.puntos1) + " " + self.jugador2 + ": " + str(self.puntos2), align="center", font=("Arial", 15, "bold"))

            if (self.bola.xcor() > 260) and (self.bola.xcor() < 280) and (self.bola.ycor() < (self.raqueta2.ycor() + 30)) and (self.bola.ycor() > (self.raqueta2.ycor() - 30)): # La bola ha golpeado la raqueta  
                self.bola.setx(260)
                self.bola.velx *= -1.1
            elif (self.bola.xcor() > -280) and (self.bola.xcor() < -260) and (self.bola.ycor() < (self.raqueta1.ycor() + 30)) and (self.bola.ycor() > (self.raqueta1.ycor() - 30)): # La bola ha golpeado la raqueta  
                self.bola.setx(-260)
                self.bola.velx *= -1.1
    
    def recibir_raqueta(self):
        # Recibimos los comandos del servidor y los añadimos a una cola
        conectado = True
        while conectado:
            try:
                self.cola.put(self.conn.recv_bytes(1))
            
            except:
                print("Connection Abborted - Un jugador se ha salido de la partida")
                conectado = False
    
    def start_bola(self):
        # Mueve la bola desde el inicio
        self.bola.goto(0,0)
        self.bola.velx = 0.5
        self.bola.vely = 0.5

    def raqueta_arriba(self):
        if self.id == 1:
            eje_y = self.raqueta2.ycor()
            if eje_y <= 180:
                eje_y += 10
                self.raqueta2.sety(eje_y)
                # Enviamos el comando (0 indica hacia arriba)
                self.conn.send_bytes((0).to_bytes(1, byteorder='big'))
        else:
            eje_y = self.raqueta1.ycor()
            if eje_y <= 180:
                eje_y += 10
                self.raqueta1.sety(eje_y)
                # Enviamos el comando (0 indica hacia arriba)
                self.conn.send_bytes((0).to_bytes(1, byteorder='big'))
                
    def raqueta_abajo(self):
        if self.id == 1:
            eje_y = self.raqueta2.ycor()
            if eje_y >= -180:
                eje_y -= 10
                self.raqueta2.sety(eje_y)
                # Enviamos el comando (1 indica hacia abajo)
                self.conn.send_bytes((1).to_bytes(1, byteorder='big'))
        else:
            eje_y = self.raqueta1.ycor()
            if eje_y >= -180:
                eje_y = eje_y - 10
                self.raqueta1.sety(eje_y)
                # Enviamos el comando (1 indica hacia abajo)
                self.conn.send_bytes((1).to_bytes(1, byteorder='big'))
    
    def raqueta_arriba_Contr(self):
        if self.id_contr == 1:
            eje_y = self.raqueta2.ycor()
            if eje_y <= 180:
                eje_y += 10
                self.raqueta2.sety(eje_y)
        else:
            eje_y = self.raqueta1.ycor()
            if eje_y <= 180:
                eje_y += 10
                self.raqueta1.sety(eje_y)
            
    def raqueta_abajo_Contr(self):
        if self.id_contr == 1:
            eje_y = self.raqueta2.ycor()
            if eje_y >= -180:
                eje_y -= 10
                self.raqueta2.sety(eje_y)
        else:
            eje_y = self.raqueta1.ycor()
            if eje_y >= -180:
                eje_y -= 10
                self.raqueta1.sety(eje_y)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
    
 