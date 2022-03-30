# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import Tk,Canvas
import random
import time
from math import floor
from multiprocessing import *
from bola_ladrillos import Bola
from barra_y_bloque_ladrillos import Barra, Bloque

class Rompeladrillos():
    def __init__(self, espectador, ventana_principal):
        """Listas que funcionarán como variables globales, contendrán objetos de la clase Bola, objetos de la clase Bloque"""
        """ y números respectivamente"""
        self.lista_bolas = []
        self.lst2 = []
        self.lst3 = []
        self.lst4 = []
        self.tamano = 15
        self.tablero = self.generar()  

        """Con esto creamos el lienzo de un cierto tamaño"""
        self.ventana = tk.Toplevel(ventana_principal)
        self.ventana.title("Rompeladrillos")
        self.c = Canvas(self.ventana, width = 705, height= 510, bg='white')
        self.c.pack()
        self.p1 = 0
        self.dibujar()
        self.bar = Barra(self.c, 200, 0, 10, espectador)
        
        self.buff_bloque()
        self.crear_bolas()
        self.romper_ventana()
    
    def zerolistmaker(self, n):
        """Crea una lista de ceros de tamaño n"""
        listofzeros = [0] * n
        return listofzeros

    def matriz_ceros(self):
        """ Crea una lista de listas de ceros utilizando la función anterior"""
        """que será nuestra matriz tablero"""
        matriz = []
        lista = []
        for x in range(self.tamano):
            lista = self.zerolistmaker(self.tamano)
            matriz.append(lista)
        return matriz

    def generar(self):
        """ utiliza la matriz de ceros anterior y cambia los ceros del borde por -1, -2 y -3 según el lado en el que esté"""
        """también les cambia el valor a 1 a todos los ceros que estén en el primer tercio de las filas, excepto los que estén en los bordes"""
        matriz = self.matriz_ceros()
        for x in range(self.tamano):
            for y in range(self.tamano):
                if x == 0 or x == self.tamano - 1:
                    matriz[x][y] = -1
                elif y == 0:
                    matriz[x][y] = -2
                elif y == self.tamano - 1:
                    matriz[x][y] = -3
                elif x < self.tamano / 3 + 1 and (matriz[x][y] == 0):
                    matriz[x][y] = 1
        return matriz
    
    def dibujar(self):
        """Esta función nos dibuja en el lienzo que hemos creado rectángulos de diferentes tamaños según el valor que tengan en la matriz tablero"""
        """También si el valor es 1 crea objetos de la clase Bloque y los añade a las listas globales descritas anteriormente"""
        for i in range(self.tamano): #DIBUJO EL TABLERO
            for j in range(self.tamano): 
                if self.tablero[i][j] == -1:
                    self.c.create_rectangle(47 * j, 34 * i, 47 * j + 47, 34 * i + 34, fill='black')
                elif self.tablero[i][j] == -2:
                    self.c.create_rectangle(0, 34 * i, 17, 34 * i + 34, fill = 'black')
                elif self.tablero[i][j] == 1:
                    p = Bloque(self.c, 17 + (j-1)*56, 34 * i, 0)
                    r = i / j ** 5
                    self.lst2.append(p)
                    self.lst4.append(p)
                    self.lst3.append(r)
                elif self.tablero[i][j] == -3:
                    self.c.create_rectangle(689, 34 * i, 705, 34 * (i + 1), fill = 'black')
    
    def buff_bloque(self):
        """Función que se repetirá cada un cierto tiempo establecido que elije un objeto de la clase Bloque aleatoriamente"""
        """y le sube en +1 su estado con el consiguiente cambio en el color del Bloque q esto conlleva"""
        estados = ['blue', 'red', 'cyan', 'yellow', 'magenta']
        z = random.randrange(len(self.lst2))
        a = self.lst2[z]
        
        if a.estad in range(6):
            self.c.itemconfig(a.bloque, fill = estados[a.estad])
            a.estad += 1
        
        self.c.after(600, self.buff_bloque)
    
    def borrar(self, x):
        """Usada para borrar los bloques una vez son destruidos"""
        p = self.lst4[x]
        self.c.delete(p.bloque)
        
    def debuff_bloque(self, z):
        """Función usada en las funciones de chocar de la clase Bola, en el monento en el que se produzca un impacto"""
        """con un bloque determinado esta función le baja -1 su estado y le cambia al color que le corresponda"""
        estados = ['grey', 'blue', 'red', 'cyan', 'yellow']
        a = self.lst2[z]
        if a.estad in range(1, 6):
            self.c.itemconfig(a.bloque, fill = estados[a.estad - 1])
            a.estad -= 1
    
    def crear_bolas(self):
        """Otra función que se llama constantemente a sí misma cada cierto tiempo que crea un objeto de la clase Bola"""
        # q = random.randrange(5, 15)
        u = Bola(self.c, 8, 180, 450, 190, 460, 1, -1, 0, self)
        self.lista_bolas.append(u)
        u.movimiento()
        
        self.c.after(10000, self.crear_bolas)
    
    def romper_ventana(self):
        """Cuando la lista global lista_bolas se queda sin ningún elemento destruye el lienzo y acaba la partida"""
        """Se llama a sí misma para ejecutarse cada vez que una bola se mueve"""
        if len(self.lista_bolas) == 0:
            self.bar.client.disconnect()
            self.ventana.destroy()
        
        self.c.after(1, self.romper_ventana)
       
