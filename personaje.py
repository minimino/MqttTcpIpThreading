from bomba import Bomba
from math import floor

class Personaje:
    def __init__(self,nombre,numero,posicionx,posiciony,numero_bombas,activas,radio,modificadores ,velocidad ,estado_vital,numero_victorias, tablero):
        self.name = nombre
        self.num = numero
        self.x = posicionx
        self.y = posiciony
        self.nbomb = numero_bombas
        self.activas = activas
        self.mod = modificadores
        self.speed = velocidad
        self.alive = estado_vital
        self.vict = numero_victorias
        self.radio = radio
        self.tablero = tablero.tablero
        self.tableroObj = tablero

    def get_bomb(self): #Coge modificador de bomba
        self.nbomb += 1
        self.mod.append("b")
        print("jugador",self.name,"coge bomba")
        self.tablero[floor(self.x)][floor(self.y)] = 0
        
    def get_speed(self): #Coge el modificador de velocidad
        self.speed += 1
        self.mod.append("v")
        print("jugador",self.name,"aumenta su velocidad")
        self.tablero[floor(self.x)][floor(self.y)] = 0
    
    def get_range(self): #Coge el modificador de radio
        self.radio += 1
        self.mod.append("r")
        print("jugador",self.name,"aumenta su radio")
        self.tablero[floor(self.x)][floor(self.y)] = 0
        
    def plantar(self): #El jugador planta una bomba debajo de él
        rx = floor(self.x)  #El floor es la coordenada del jugador en la matriz del tablero. Ej: Si el jugador esta en (5.4,6.7), esta en la posicion (5,7) del tablero (matriz). Y ahi pone su bomba
        ry = floor(self.y)
        if self.activas < self.nbomb:
            b = Bomba(self.tableroObj,self.radio,rx,ry,self)
            b.poner()
            self.activas += 1

    def up(self): #El jugador se mueve hacia arriba con una cierta velocidad. Puede salir de la bomba que acaba de poner, pero no puede atravesar bombas, casillas negras ni casillas verdes (debe romperlas con la bomba)
        siguiente = self.tablero[floor(self.x)][floor(self.y  - self.speed*0.1)]
        siguiente_libre = siguiente != -2 and siguiente != -3 #Hemos de ver si la casilla no es ni verde ni negra
        
        if siguiente_libre:
            if type(self.tablero[floor(self.x)][floor(self.y)]) != str and self.tablero[floor(self.x)][floor(self.y)] > 0: #Si estamos encima de una bomba podremos movernos libremente (Nota: Solo es posible estar encima de una bomba si acabas de ponerla)
                self.y = self.y - self.speed*0.1
            else:
                if siguiente == 0 or siguiente in self.tableroObj.modificadores.keys():# Si es una casilla blanca o un modificador nos moveremos sin problema
                    self.y = self.y - self.speed*0.1
                    
    def down(self): #COMPROBAR
        siguiente = self.tablero[floor(self.x)][floor(self.y  + self.speed*0.1)]
        siguiente_libre = siguiente != -2 and siguiente != -3
        if siguiente_libre:
            if type(self.tablero[floor(self.x)][floor(self.y)]) != str and self.tablero[floor(self.x)][floor(self.y)] > 0:
                self.y = self.y + self.speed*0.1
            else:
                if siguiente == 0 or siguiente in self.tableroObj.modificadores.keys():
                    self.y = self.y + self.speed*0.1

    def left(self): #COMPROBAR
        siguiente = self.tablero[floor(self.x - self.speed*0.1)][floor(self.y)]
        siguiente_libre = siguiente != -2 and siguiente != -3
        if siguiente_libre:
            if type(self.tablero[floor(self.x)][floor(self.y)]) != str and self.tablero[floor(self.x)][floor(self.y)] > 0:
                self.x = self.x - self.speed*0.1 
            else:
                if siguiente == 0 or siguiente in self.tableroObj.modificadores.keys():
                    self.x = self.x - self.speed*0.1 
            
    def right(self): #COMPROBAR
        siguiente = self.tablero[floor(self.x + self.speed*0.1)][floor(self.y)]
        siguiente_libre = siguiente != -2 and siguiente != -3
        if siguiente_libre:
            if type(self.tablero[floor(self.x)][floor(self.y)]) != str and self.tablero[floor(self.x)][floor(self.y)] > 0:
                self.x = self.x + self.speed*0.1
            else:
                if siguiente == 0 or siguiente in self.tableroObj.modificadores.keys():
                    self.x = self.x + self.speed*0.1