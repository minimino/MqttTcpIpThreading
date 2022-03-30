from threading import Thread
from personaje import Personaje
import tkinter as tk
from tkinter import Tk, Canvas, PhotoImage
from math import floor

class Tablero:
    def __init__(self, tablero, posiciones, num_jugadores, lista_nombres, mi_nombre, cliente, ventana_principal):
        self.num_jugadores = num_jugadores
        self.cliente = cliente
        self.ventana = tk.Toplevel(ventana_principal)
        self.modificadores = {'b' : 'get_bomb()', 'v' : 'get_speed()', 'r' : 'get_range()'}
        self.ventana.title(mi_nombre)
        self.canvas = Canvas(self.ventana, width = 30*(5 + 2 * num_jugadores), height= 30*(5 + 2 * num_jugadores))
        self.ventana.geometry(str(30*(5 + 2 * num_jugadores))+"x"+str(30*(5 + 2 * num_jugadores)))
        self.canvas.pack()
        self.canvas.bind_all("<Key>", self.mover) 
        self.canvas.place(x = 0, y = 0)
        self.lista_jugadores_dibujados = []
        self.tablero = tablero
        self.lista_jugadores = [ self.crear_personaje(j[0], j[1], posiciones) for j in lista_nombres ]
        self.lista_bombas = []
        self.foto_coronavirus= PhotoImage(file = 'images/coronavirus.png')
        self.foto_emoji = PhotoImage(file = "images/emoji.png")
        self.dibujar_tablero()
        self.dibujar_jugadores()
        self.yo = [ i for i in self.lista_jugadores if i.name == mi_nombre ][0]
        Thread(target = self.recibir_y_act).start()
        
    def recibir_y_act(self): #Recibe una accion del servidor, busca el jugador que la ha hecho y la ejecuta
        while True:
            accion = self.cliente.recv() 
            valido = [ j for j in self.lista_jugadores if j.num == accion[1] ][0] #Vemos a ver que personaje es el que corresponde con el numero de personaje que ha llegado del servidor y ejecutamos dicha accion
            self.mover_personaje_ajeno(accion[0], valido)
    
    def crear_personaje(self, nombre, numero, posiciones):
        return Personaje(nombre, numero, posiciones[numero - 1][0], posiciones[numero - 1][1], 1, 0, 3, [], 1, True, 0, self)
    
    def dibujar_tablero(self):
        #Borramos todo el tablero anterior y dibujamos uno nuevo
        self.canvas.delete("all")
        elems_fijos = {0:"white", -3:"black", -2:"green"}
        
        for i in range(0,len(self.tablero)): #DIBUJO EL self.tablero
            for j in range(0,len(self.tablero)):
                valor_pos = self.tablero[i][j]
                
                if valor_pos in elems_fijos.keys():
                    self.canvas.create_rectangle(30*i, 30*j, 30*i+30,30*j+30, fill=elems_fijos[valor_pos])                    
                elif valor_pos in self.modificadores.keys():
                     self.canvas.create_rectangle(30*i, 30*j, 30*i+30,30*j+30, fill="white")
                     self.canvas.create_oval(30*i + 5,30*j + 5, 30*i+30 - 5,30*j+30 - 5, fill="yellow")
                     self.canvas.create_text(30*i + 5+10, 30*j + 5+10, text = valor_pos.upper())
                elif valor_pos > 0:
                    self.canvas.create_rectangle(30*i, 30*j, 30*i+30, 30*j+30, fill="white")
                    self.canvas.create_image(30*i, 30*j, image = self.foto_coronavirus, anchor = "nw")

    def mover_personaje_ajeno(self, accion, personaje): #Con W,D,S,A mueves a tu personaje, esta funcion mueve al que no eres tu, segun lo que le llega del servidor
        valor_pos = self.tablero[floor(personaje.x)][floor(personaje.y)]
        acciones = [personaje.up, personaje.down, personaje.left, personaje.right, personaje.plantar]

        if accion in range(1, 6): 
            acciones[accion - 1]()
            if accion == 5:
                self.dibujar_tablero()
            elif valor_pos in self.modificadores.keys():
                exec("personaje." + self.modificadores[valor_pos])
                self.dibujar_tablero()
        
        self.dibujar_jugadores()  
    
    def dibujar_jugadores(self): #DIBUJA SOLO LOS JUGADORES
        for elemento in self.lista_jugadores_dibujados:
            self.canvas.delete(elemento) #Borro todo lo relacionado con los jugadores, no el tablero
        
        self.lista_jugadores_dibujados = [] #Borro la lista anterior una vez borrado los elementos de ella
        
        for jugador in self.lista_jugadores: #Dibujo a los jugadores
            if jugador.alive:
                o = self.canvas.create_image(30*jugador.x - 15, 30*jugador.y - 15,image = self.foto_emoji, anchor = "nw")
                t = self.canvas.create_text(30*jugador.x,30*jugador.y - 8, text = jugador.name, fill = "black")
                self.lista_jugadores_dibujados.append(o)
                self.lista_jugadores_dibujados.append(t)
    
    def mover(self, event): #Mueve a tu propio jugador
        kp = event.keysym
        valor_pos = self.tablero[floor(self.yo.x)][floor(self.yo.y)]
        acciones = {'w' : (1, self.yo.up), 'W' : (1, self.yo.up), 'Up' : (1, self.yo.up), 's' : (2, self.yo.down), 'S' : (2, self.yo.down), 'Down' : (2, self.yo.down), 'a' : (3, self.yo.left),  'A' : (3, self.yo.left), 'Left' : (3, self.yo.left), 'd' : (4, self.yo.right), 'D' : (4, self.yo.right), 'Right' : (4, self.yo.right), 'space' : (5, self.yo.plantar)}    
        
        if kp in acciones.keys(): # Ejecutamos una acción según la tecla que haya pulsado el cliente
            acciones[kp][1]()
            print("He presionado " + kp)
            codigo = (acciones[kp][0], self.yo.num)
            self.cliente.send(codigo)
            
            if kp == "space":
                self.dibujar_tablero()
            elif valor_pos in self.modificadores.keys():
                exec("self.yo." + self.modificadores[valor_pos])
                self.dibujar_tablero()
                
            self.dibujar_jugadores()        
                