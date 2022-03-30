from threading import Timer

class Bomba:
    def __init__(self, tablero, radio, posicionx, posiciony, dueno): #Estos son los atributos de una bomba
        self.tablero = tablero
        self.rad = radio
        self.x = posicionx
        self.y = posiciony
        self.dueno = dueno
    
    def explotar(self):
        """
        Dado una bomba la hace explotar. Esto rompe la primera casilla verde a su alcance, mata a los jugadores en el rango y hace desaparecer la bomba del mapa.        
        """
        print("Y HACE PUMMMMMMMM, AYY YA ESTA AQUI LA GUERRA")
        bloques_afectados = [(self.x,self.y)]
        
        # (1, 0) explota hacia la derecha, (-1,0) hacia la izquierda, (0, 1) hacia arriba...
        for (i, j) in [(1,0), (-1, 0), (0, 1), (0, -1)]:
            r = 1
            while r <= self.rad:
                valor_pos = self.tablero.tablero[self.x + i*r][self.y + j*r]
                if valor_pos == 0:
                    bloques_afectados.append((self.x + i*r, self.y + j*r))
                elif valor_pos in self.tablero.modificadores.keys():  #Destruye las mejoras
                    bloques_afectados.append((self.x + i*r, self.y + j*r))
                    self.tablero.tablero[self.x + i*r][self.y + j*r] = 0
                elif valor_pos == -2: #Las casillas verdes se destruye la primera que toca por direccion, y no atraviesan mas allá
                    bloques_afectados.append((self.x + i*r, self.y + j*r))
                    self.tablero.tablero[self.x + i*r][self.y + j*r] = 0
                    break
                elif valor_pos == -3: #Las casillas negras no las explota ni atraviesa
                    break
                r += 1
        
        self.tablero.tablero[self.x][self.y] = 0 #Desaparece la bomba del mapa cuando explota
        self.dueno.activas -= 1 #El dueño pasa a tener una bomba menos activa

        lx = [ i[0] for i in bloques_afectados ] #Son todas las casillas en la cruz horizontal afectadas
        ly = [ i[1] for i in bloques_afectados ] #Casillas en vertical afectadas
        
        maxx, minx = max(lx), min(lx)  #Vemos hasta dónde llega el rango de las explosiones
        maxy, miny = max(ly), min(ly)
        
        for jugador in self.tablero.lista_jugadores:#Vemos si algun jugador está en la cruz de la explosión
            if minx <= jugador.x and jugador.x < maxx + 1 and self.y <= jugador.y and jugador.y < self.y + 1:
                jugador.alive = False #Cruz horizontal
            elif miny <= jugador.y and jugador.y < maxy + 1 and self.x <= jugador.x and jugador.x < self.x + 1:
                jugador.alive = False #Cruz vertical
       
        self.tablero.lista_bombas.remove(self) #Eliminamos la bomba de la lista de bombas puestas
        self.tablero.dibujar_tablero() #Dibujamos el mapa de nuevo sin la bomba
        self.tablero.dibujar_jugadores() #Dibujamos a los jugadores de nuevo
 
    def poner(self): #El dueño pone una bomba en su posición
        lb = self.tablero.lista_bombas
        
        if self.dueno.alive: #Solo se pueden poner bombas si estás vivo
            self.tablero.tablero[self.x][self.y] = self.dueno.num
            lb.append(self)
            t = Timer(3, self.explotar)
            t.start() #La bomba explota automáticamente 3 segundos después de ponerla
