import turtle

class Pong_offline():
    def __init__(self):
        
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
        self.raqueta1.color("white")   # Color blanco de la raqueta
        self.raqueta1.speed(0)         # Velocidad movimiento raqueta
        self.raqueta1.shape("square")  # Forma de la raqueta
        self.raqueta1.shapesize(3,0.75)
        self.raqueta1.goto(-270, 0)
        
        # Raqueta 2
        self.raqueta2 = turtle.Turtle()
        self.raqueta2.penup()
        self.raqueta2.color("white")   # Color blanco de la raqueta
        self.raqueta2.speed(0)         # Velocidad movimiento raqueta
        self.raqueta2.shape("square")  # Forma de la raqueta
        self.raqueta2.shapesize(3,0.75)
        self.raqueta2.goto(270, 0)

        # Bola
        self.bola = turtle.Turtle()
        self.bola.penup()
        self.bola.color("white")   # Color blanco de la bola
        self.raqueta2.speed(0)     # Velocidad movimiento raqueta
        self.bola.shape("circle")  # Forma de la bola
        self.bola.shapesize(0.5,0.5)
        self.bola.goto(0,0)
        self.bola.velx = 0.5
        self.bola.vely = 0.5
        
        # Marcador de puntuación
        self.marcador = turtle.Turtle()
        self.marcador.hideturtle()
        self.marcador.penup()
        self.marcador.color("white")   # Color blanco del marcador
        self.marcador.goto(0, 165)
        self.marcador.write("Jugador 1: " + str(self.puntos1) + "   Jugador 2: " + str(self.puntos2), align="center", font=("Arial", 15, "bold")) # Texto marcador

        # Botones para ejecutar los movimientos de las raquetas
        self.pantalla.listen()
        self.pantalla.onkeypress(self.raqueta1_arriba, "w")  # 'w' para subir raqueta 2
        self.pantalla.onkeypress(self.raqueta1_abajo, "s")   # 's' para bajar raqueta 2
        self.pantalla.onkeypress(self.raqueta2_arriba, "Up") # Flecha arriba para subir raqueta 2
        self.pantalla.onkeypress(self.raqueta2_abajo, "Down") # Flecha abajo para subir raqueta 2

        # Movimientos de la bola
        while True:
            self.pantalla.update()   # Actualizar pantalla       
            self.bola.setx(self.bola.xcor() + self.bola.velx)
            self.bola.sety(self.bola.ycor() + self.bola.vely)
           
            if self.bola.ycor() > 200: # La bola ha llegado al techo
                self.bola.sety(200)
                self.bola.vely *= -1
            elif self.bola.ycor() < -200: # La bola ha llegado al suelo
                self.bola.sety(-200)
                self.bola.vely *= -1
           
            if self.bola.xcor() > 300: # La bola ha llegado al lado derecho
                self.bola.goto(0,0)
                self.bola.velx = -0.1
                self.puntos1 += 1
                self.marcador.clear()
                self.marcador.write("Jugador 1: " + str(self.puntos1) + "   Jugador 2: " + str(self.puntos2), align="center", font=("Arial", 15, "bold"))
            elif self.bola.xcor() < -300: # La bola ha llegado al lado izquierdo
                self.bola.goto(0,0)
                self.bola.velx = 0.1
                self.puntos2 += 1
                self.marcador.clear()
                self.marcador.write("Jugador 1: " + str(self.puntos1) + "   Jugador 2: " + str(self.puntos2), align="center", font=("Arial", 15, "bold"))

            if (self.bola.xcor() > 260) and (self.bola.xcor() < 280) and (self.bola.ycor() < (self.raqueta2.ycor() + 30)) and (self.bola.ycor() > (self.raqueta2.ycor() - 30)): # La bola ha golpeado la raqueta
                self.bola.setx(260)
                self.bola.velx *= -1.1
            elif (self.bola.xcor() > -280) and (self.bola.xcor() < -260) and (self.bola.ycor() < (self.raqueta1.ycor() + 30)) and (self.bola.ycor() > (self.raqueta1.ycor() - 30)):  # La bola ha golpeado la raqueta  
                self.bola.setx(-260)
                self.bola.velx *= -1.1
                
            
     # Función para mover la raqueta 1 hacia arriba
    def raqueta1_arriba(self):
        eje_y = self.raqueta1.ycor()
        if eje_y <= 180:   # Se puede mover hasta una longitud máxima de 180 por el tablero
            eje_y = eje_y + 10     # Se mueven posiciones de 10 en 10
            self.raqueta1.sety(eje_y)
            
    # Función para mover la raqueta 1 hacia abajo
    def raqueta1_abajo(self):
        eje_y = self.raqueta1.ycor()
        if eje_y >= -180:  # Se puede mover hasta una longitud máxima de -180 por el tablero
            eje_y = eje_y - 10     # Se mueven posiciones de 10 en 10
            self.raqueta1.sety(eje_y)
    
    # Función para mover la raqueta 2 hacia arriba
    def raqueta2_arriba(self):
        eje_y = self.raqueta2.ycor()
        if eje_y <= 180:   # Se puede mover hasta una longitud máxima de 180 por el tablero
            eje_y = eje_y + 10     # Se mueven posiciones de 10 en 10
            self.raqueta2.sety(eje_y)
            
    # Función para mover la raqueta 2 hacia abajo
    def raqueta2_abajo(self):
        eje_y = self.raqueta2.ycor()
        if eje_y >= -180:  # Se puede mover hasta una longitud máxima de -180 por el tablero
            eje_y = eje_y - 10     # Se mueven posiciones de 10 en 10
            self.raqueta2.sety(eje_y)

