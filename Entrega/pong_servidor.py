from multiprocessing import Process, Manager
from multiprocessing import AuthenticationError
import pickle

def reenvio_pong(conn, conn_oponente):
    enviando = True
    while enviando:
        try:
            # Recibimos un byte y lo reenviamos
            comando = conn.recv_bytes(1)
            conn_oponente.send_bytes(comando)
        except:
            print('Se ha roto la conexión de pong')
            enviando = False

    conn.close()

def esperar_listo(conn, lista_nombres):
    id, conexion = conn
    conexion.send_bytes((id).to_bytes(1, byteorder='big')) # Enviamos su id al cliente
    lista_nombres[id] = conexion.recv_bytes(35) # Recibimos el nombre del cliente

def crear_entorno_pong(listener_pong):
    while True:
        lista_jugadores_pong = []
        i_disp = [0, 1]

        while len(i_disp) > 0:
            try:
                print('Esperando conexiones nuevas...')
                conn_pong = listener_pong.accept()
                print('He aceptado una conexión de ', listener_pong.last_accepted)
            except AuthenticationError:
                print ('Conexión rechazada: contraseña incorrecta')
        
            i = i_disp.pop(0)
            lista_jugadores_pong.append((i, conn_pong))
        
        lista_nombres = Manager().list(['', ''])
        
        # Creamos un proceso para cada cliente que espera a que estén listos
        p1 = Process(target = esperar_listo, args=(lista_jugadores_pong[0], lista_nombres))
        p2 = Process(target = esperar_listo, args=(lista_jugadores_pong[1], lista_nombres))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        
        for id, conexion in lista_jugadores_pong:
            print("Ya estamos todos")
            print('Creando nuevos procesos para el cliente...')
            id_oponente = 1 - id
            # Enviamos el nombre
            conexion.send_bytes(lista_nombres[id_oponente])
            # Iniciamos el proceso para reenviar comandos
            Process(target=reenvio_pong, args=(conexion, lista_jugadores_pong[id_oponente][1])).start()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
  