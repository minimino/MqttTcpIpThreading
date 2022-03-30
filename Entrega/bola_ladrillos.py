class Bola:
    def __init__(self, c, vel, x1, y1, x2, y2, dirx, diry, etdo, rompeladrillos):
        """Esta es la primera clase que creamos, le proporcionamos 9 atributos, un lienzo que crearemos luego, una velocidad,"""
        """4 atributos de posición, 2 de dirección y un estado, además de otro atributo para generar una círculo en el lienzo"""
        """automáticamente en cuanto se cree un objeto de esta clase"""
        self.rompeladrillos = rompeladrillos
        self.vel = vel
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.dirx = dirx
        self.diry = diry
        self.c = c
        self.etdo = etdo
        self.ball = c.create_oval(self.x1, self.y1, self.x2, self.y2, fill = 'black')

    def chocar_bloque_izquierda(self):
        """Función dentro de la clase, recorre todas las posiciones de la matriz tablero, coje las que tienen un 1 y ve si el elemento que está"""
        """a su izquierda es un 0, si cumple las 2 comprueba si la posición de un objeto de la clase Bola coincide con el lateral izquierdo del bloque"""
        """si coincide cambia su sentido en el eje x y le baja en -1 el estado del bloque"""
        for x in range(self.rompeladrillos.tamano):
            for y in range (self.rompeladrillos.tamano):
                if self.rompeladrillos.tablero[x][y] == 1 and self.rompeladrillos.tablero[x][y-1] == 0:
                    if self.x1 + 5 == 17 + 56 * (y - 1) and self.y1 + 5  >= 34 + 34 * (x - 1) and self.y1 + 5 < 34 + 34 * x:
                        self.dirx = -self.dirx
                        if self.rompeladrillos.lst4[self.borra(x,y)].estad <= 0:
                            self.rompeladrillos.tablero[x][y] = 0
                            self.rompeladrillos.borrar(self.borra(x, y))
                            print(x,y,'chocar por derecha')
                        elif self.rompeladrillos.lst4[self.borra(x,y)].estad > 0:
                            self.rompeladrillos.debuff_bloque(self.borra(x, y))
                            print(self.rompeladrillos.lst4[self.borra(x,y)].estad)
                       
    def chocar_bloque_abajo(self):
        """Misma función que la anterior, pero en este caso es la parte inferior del bloque la que se compara con la posicion de la bola"""
        for x in range(self.rompeladrillos.tamano):
            for y in range(self.rompeladrillos.tamano):
                if self.rompeladrillos.tablero[x][y] == 1 and self.rompeladrillos.tablero[x+1][y] == 0:
                    if self.y1 + 5 == 34 + 34 * x and self.x1 + 5 >= 17 + 56 * (y - 1) and self.x1 + 5 < 17 + 56 * y:
                        self.diry = -self.diry 
                        if self.rompeladrillos.lst4[self.borra(x,y)].estad <= 0:
                            self.rompeladrillos.tablero[x][y] = 0
                            self.rompeladrillos.borrar(self.borra(x, y))
                            print(x,y,'chocar por abajo')
                        elif self.rompeladrillos.lst4[self.borra(x,y)].estad > 0:
                            self.rompeladrillos.debuff_bloque(self.borra(x, y))
                            print(self.rompeladrillos.lst4[self.borra(x,y)].estad)

                        
    def chocar_bloque_derecha(self):
        """Igual que la anterior pero con el lado derecho del bloque"""
        """En cada una de estas 4 funciones se añade el punto que forma el pico que le corresponde a su lado"""
        for x in range(self.rompeladrillos.tamano):
            for y in range(self.rompeladrillos.tamano):
               if self.rompeladrillos.tablero[x][y] == 1 and self.rompeladrillos.tablero[x][y+1] == 0:
                   if self.x1 + 5 == 17 + 56 * y and self.y1 + 5 > 34 + 34 * (x - 1) and self.y1 + 5 < 34 + 34 * x:
                       self.dirx = -self.dirx
                       if self.rompeladrillos.lst4[self.borra(x,y)].estad <= 0:
                           self.rompeladrillos.tablero[x][y] == 0
                           self.rompeladrillos.borrar(self.borra(x, y))
                           print(x,y,'chocar por izquierda')
                           print(self.rompeladrillos.lst4[self.borra(x,y)].estad)
                       elif self.rompeladrillos.lst4[self.borra(x,y)].estad > 0:
                           self.rompeladrillos.debuff_bloque(self.borra(x, y))
                           print(self.rompeladrillos.lst4[self.borra(x,y)].estad)
                  
 
    def chocar_bloque_arriba(self):
        """igual que el anterior pero con el lado de arriba"""
        for x in range(self.rompeladrillos.tamano):
            for y in range(self.rompeladrillos.tamano):
               if self.rompeladrillos.tablero[x][y] == 1 and self.rompeladrillos.tablero[x-1][y] == 0:
                   if self.y1 + 5 == 34 + 34 * ( x - 1) and self.x1 + 5 > 17 + 56 * (y - 1) and self.x1 + 5 <= 17 + 56 * y:
                       self.diry = -self.diry
                       if self.rompeladrillos.lst4[self.borra(x,y)].estad <= 0:
                           self.rompeladrillos.borrar(self.borra(x, y))
                           self.rompeladrillos.tablero[x][y] = 0
                           print(x,y,'chocar por arriba')
                       elif self.rompeladrillos.lst4[self.borra(x,y)].estad > 0:
                           self.rompeladrillos.debuff_bloque(self.borra(x, y))
                           print(self.rompeladrillos.lst4[self.borra(x,y)].estad)
  

    def movimiento(self):
        """Es la función más importante del juego, primero ejecuta las 4 funciones anteriores por si hay un choque con algun bloque"""
        """Luego tiene en cuenta por si hay un choque contra alguno de los bordes del lienzo, es decir, los corresponientes a los valores"""
        """negativos de la matriz tablero, ejecuta un movimiento con la función move() cambiando una de las direcciones para simular el choque"""
        """o sin cambiar ninguna dirección si no está cerca de ningun borde, siguiendo su movimiento natural"""
        """Al final de cada condicional se usa la función after(), que vuelve a ejecutar la función movimiento, después de un cierto tiempo"""
        """a este tiempo le llamaremos velocidad de la Bola"""                  
        self.chocar_bloque_abajo()
        self.chocar_bloque_arriba()
        self.chocar_bloque_derecha()
        self.chocar_bloque_izquierda()
        if self.x1 + 5 == 17 or self.x1 + 5 == 688:
            self.c.move(self.ball, -self.dirx, self.diry)
            self.x1 = self.x1 - self.dirx
            self.y1 = self.y1 + self.diry
            self.dirx = -self.dirx
            self.c.after(self.vel, self.movimiento)
        elif self.y1 + 5 == 34:
            self.c.move(self.ball, self.dirx, -self.diry)
            self.x1 = self.x1 + self.dirx
            self.y1 = self.y1 - self.diry
            self.diry = -self.diry
            self.c.after(self.vel, self.movimiento)
        elif self.x1 + 5 > self.posicion_barra() and self.x1 + 5 < self.posicion_barra() + 90 and self.y1 + 15 > 466 and self.y1 + 15 < 476:
            self.c.move(self.ball, self.dirx, -self.diry)
            self.x1 = self.x1 + self.dirx
            self.y1 = self.y1 - self.diry
            self.diry = -self.diry
            self.c.after(self.vel, self.movimiento)
        elif self.y1 + 5 > 476:
            self.rompeladrillos.lista_bolas.pop()
        else:
            self.c.move(self.ball, self.dirx, self.diry)
            self.x1 = self.x1 + self.dirx
            self.y1 = self.y1 + self.diry
            self.c.after(self.vel, self.movimiento)
            
            
    def posicion_barra(self):
        """Esta función solo sirve para relacionar una función de otra clase con esta"""
        return self.rompeladrillos.bar.posicion()
    

    def borra(self, x, y):
        """Busca en una lista de objetos de la clase Bloque, que se creará más tarde, un cierto objeto que estará localizado por la posición en la matriz tablero"""
        """Si la posición de ese bloque viene establecido por x e y, la posición del Bloque en la lista vendrá determinado por el número x / y ** 5"""
        """Esto lo hacemos para que cada bloque quede determinado por un solo número creado con la posición x e y"""
        k = self.rompeladrillos.lst3.index(x / y ** 5)
        return k
        