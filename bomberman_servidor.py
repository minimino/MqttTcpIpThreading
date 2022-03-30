import random
import pickle
from multiprocessing import Process, Manager, Queue, AuthenticationError

def generar_tablero(numero_jugadores):
    tablero_sin_limpiar = generar_tablero_sin_limpiar(numero_jugadores) # Creamos un tablero donde es posible que el jugador no pueda moverse
    posiciones_iniciales = generar_posiciones_iniciales(numero_jugadores) # Creamos las posiciones iniciales
    tablero_sin_mejoras = limpiar_posiciones_iniciales(tablero_sin_limpiar, posiciones_iniciales) # Limpiamos el tablero para permitir a los jugadores que se puedan mover y romper bloques en sus posiciones iniciales
    tablero = mejora_spawn_aleatorio(tablero_sin_mejoras, numero_jugadores * 2) # Añadimos los modificadores
    
    return tablero, posiciones_iniciales

def mejora_spawn_aleatorio(tablero, cantidad):
    vueltas = 0
    while vueltas < cantidad: 
        i, j = 0, 0
        while tablero[i][j] != 0: # Buscamos una posición libre
            i = random.randint(0,len(tablero)-1)
            j = random.randint(0,len(tablero)-1)
        tablero = mejora_spawn(tablero,i,j)
        vueltas += 1
        
    return tablero

def mejora_spawn(tablero, posicionx, posiciony):
    tab = tablero
    mejoras = ["r", "b", "v"] # Mejoras disponibles
    n = random.randint(0,2) # Cogemos una mejora aleatoriamente
    tab[posicionx][posiciony] = mejoras[n] # La metemos en el tablero

    return tab

def generar_tablero_sin_limpiar(num_player):
    valor = 5 + 2 * num_player
    tab = matriz_ceros(valor, valor)
    for i in range(valor):
        for j in range(valor):
            if i == 0 or j == 0 or i == 4 + 2 * num_player or j == 4 + 2 * num_player or (i % 2 == 0 and j % 2 == 0):
                # Estamos en el borde del tablero por lo que ponemos una casilla negra
                tab[i][j] = -3
            else:
                k = random.randrange(100)
                if k < 75:
                    # Con una probabilidad del 75% se pone una casilla verde
                    tab[i][j] = -2
                   
    return tab
        
def generar_posiciones_iniciales(num_players):
    l = []
    for x in range(num_players):
        i, j = 0, 0
        
        while i%2 == 0 or j%2 == 0:
            i = random.randint(1, 3 + 2 * num_players)
            j = random.randint(1, 3 + 2 * num_players)
            
            """ Para evitar solapamiento de nacimientos """
            # if (i, j) in l:
                # i, j = 0, 0
                
        l.append((i,j))

    return l

def limpiar_posiciones_iniciales(tablero, posiciones):
    for posicion in posiciones: # Para cada posición inicial...
        tablero = limpiar_cuadrado(posicion, tablero)
        
    return tablero
    
def limpiar_cuadrado(posicion, tablero):
    tab = tablero
    i = posicion[0]
    j = posicion[1]
    
    for x in [i - 1, i, i + 1]:
        for y in [j - 1,j,j + 1]:
            if tablero[x][y] == -2: # Eliminamos cuadrados verdes alrededor de la posición inicial del jugador
                tab[x][y] = 0           
    
    return tab

def zerolistmaker(n):
    # Devuelve una lista de ceros
    listofzeros = [0] * n
    return listofzeros 

def matriz_ceros(n, m):
    # Devuelve una matriz de ceros
    matriz = []
    lista = []
    
    for x in range(n):
        lista = zerolistmaker(m)
        matriz.append(lista)
    
    return matriz

def recibir_y_reenviar(lista_conexiones, conexion, numero_de_jugador):
    while True:
        accion = conexion.recv()
        for con in lista_conexiones:
            if con[1] != numero_de_jugador:
                con[0].send(accion)
        
def ordenar_segunda_coordenada(lista): 
    # Sabemos que los jugadores tienen cada uno un numero 1,2,3,4...
    # Esta función ordena una lista de tuplas según el orden en la segunda coordenada
    lista_ordenada = []

    for i in range(1, len(lista) + 1):
        for jugador in lista:
            if jugador[1] == i:
                lista_ordenada.append(jugador)
        
    return lista_ordenada
                
def atender_jugador_no_empezado(antesala, conexion, numero_jugador, conexiones, alguien_listo):
    # Recibimos el nombre del cliente
    nombre_bin = conexion.recv_bytes(35)
    nombre = pickle.loads(nombre_bin).strip()
    # Lo añadimos a la lista de jugadores 
    anadir = (nombre, numero_jugador, False)
    antesala.append(anadir)
    # Esperamos a que el cliente esté listo
    conexion.recv_bytes(1)
    antesala.remove(anadir)
    # Indicamos que el cliente está listo
    anadir_listo = (nombre, numero_jugador, True)
    if numero_jugador == 1:
        alguien_listo.put(1) # Si es el primer jugador añade a la cola un 1
        
    antesala.append(anadir_listo)
    
    print(antesala)

def aceptar_conexiones_bomberman(servidor, antesala, conexiones, alguien_listo):
    numero_jugador = 1
    print("Aceptando conexiones de bomberman")
    while True:
        try:
            conn = servidor.accept()
            conexiones.append((conn, numero_jugador))
            print("Conexión de bomberman aceptada de", servidor.last_accepted)
            Process(target = atender_jugador_no_empezado, args =(antesala, conn, numero_jugador, conexiones, alguien_listo)).start()
            numero_jugador += 1
        except AuthenticationError:
            print ('Conexión rechazada: contraseña incorrecta')

def crear_entorno_bomberman(list_bomberman):
    lista_procesos = []
    manager = Manager()
    antesala = manager.list()
    lista_jugadores = manager.list()
    lista_conexiones = manager.list()
    alguien_listo = Queue()
    
    # Aceptamos conexiones
    rec_conex = Process(target = aceptar_conexiones_bomberman, args = (list_bomberman, antesala, lista_conexiones, alguien_listo))
    rec_conex.start()
    
    # Esperamos a que el primer jugador esté listo
    alguien_listo.get(True)
    
    while True:
        # Comprobamos si todos los jugadores están listos
        if antesala:
            todos_listos = antesala[0][2]  
            
            for jugador in antesala:
                todos_listos = todos_listos and jugador[2]
            
            if todos_listos:
                rec_conex.terminate()
                for jugadores_listos in antesala: #Solo cuando todos los jugadores esten listos
                    anadir = (jugadores_listos[0], jugadores_listos[1]) #Su nombre y su numero
                    lista_jugadores.append(anadir)  
                break

    print("¡Todos están listos para jugar al bomberman!")
    print ("Jugadores: ", lista_jugadores)

    # Cogemos las dos primeras coordenadas de los elementos de antesala
    lista_jugadores = [ (j[0], j[1]) for j in antesala ]
    lista_jugadores = ordenar_segunda_coordenada(lista_jugadores)

    numero_jugadores = len(lista_jugadores)
    tablero, posiciones = generar_tablero(numero_jugadores)
    mandar = [tablero, posiciones, numero_jugadores, lista_jugadores]
    
    for conexion, num_jugador in lista_conexiones: #Mando la lista de cacharros
        q = Process(target = recibir_y_reenviar, args = (lista_conexiones, conexion, num_jugador))
        q.start()
        lista_procesos.append(q)
        conexion.send(mandar + [num_jugador])
    
    # Evitamos que se cierre el proceso principal (si no se borrarían todas las variables)
    for proceso in lista_procesos:
        proceso.join()
    
    