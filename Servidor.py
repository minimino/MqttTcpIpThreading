from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Manager
from time import sleep
from datetime import datetime, timedelta
from notificaciones import Notificaciones
from bomberman_servidor import crear_entorno_bomberman
from pong_servidor import crear_entorno_pong
import pickle

def elim_conexion(id, lista, semaforo):    # Si un cliente se desconecta lo eliminamos de la lista de conexiones
    semaforo.acquire()
    for i in range(len(lista)):
        if lista[i][0] == id:
            del lista[i]
    semaforo.release()

def reenvio_pzch(conn, lista_conexiones, id, conn_vid, conn_aud, i_disp, semaforo_i, semaforo_pzch):
    enviando = True
    while enviando:
        try:
            longitud_msj = conn.recv_bytes(10) # Intentamos recibir 10 bytes
            long_decod = int.from_bytes(longitud_msj, byteorder='big')
            if long_decod == 0: # Si longitud_msj es nula, entonces quieren jugar al rompeladrillos
                hora_inicio = datetime.now() + timedelta(0, 15) # Cogemos la hora actual y le sumamos 15 segundos
                for cliente in lista_conexiones:
                    cliente[2].acquire() # Adquirimos el semáforo para enviar todos los comandos secuencialmente
                    
                    if id != cliente[0]: # Es un espectador
                        data = pickle.dumps((4, 1, hora_inicio))
                    else: # Es un jugador
                        data = pickle.dumps((4, 0, hora_inicio))
                    
                    longitud_msj = len(data).to_bytes(10, byteorder='big')
                    
                    cliente[1].send_bytes(longitud_msj) # Enviamos el tamaño de la trna en 10 bytes
                    cliente[1].send_bytes(data) # Enviamos la terna
                    cliente[2].release()
            else:
                data = conn.recv_bytes(long_decod) # Recibimos el mensaje de tamaño longitud_msj
                for cliente in lista_conexiones:
                    if cliente[0] != id:
                        cliente[2].acquire() # Adquirimos el semáforo para enviar todos los comandos secuencialmente
                        cliente[1].send_bytes(longitud_msj)
                        cliente[1].send_bytes(data)
                        cliente[2].release()
        except: # Manejo de errores si un cliente se desconecta
            print('Se ha roto la conexión del chat y la pizarra con el cliente', id)
            enviando = False
    
    # Si el cliente se desconecta, se cierran las conexiones (se puede cerrar una conexión ya cerrada, no devuelve error)
    conn.close()
    conn_vid.close()
    conn_aud.close()
    elim_conexion(id, lista_conexiones, semaforo_pzch)     # Eliminamos al cliente de la lista de conexiones en la pizarra
    
    semaforo_i.acquire() # Añadimos una nueva id disponible
    if not id in i_disp:
        i_disp.append(id)
    semaforo_i.release()   
    
def reenvio_audio(conn, lista_conexiones, id, conn_vid, conn_pzch, i_disp, semaforo_i, semaforo_aud):
    enviando = True
    while enviando:
        try:
            data = conn.recv_bytes(2048)     # Recibimos los bytes del audio. Siempre son 2048 bytes
            
            for cliente in lista_conexiones:    # Reenvío del audio a todos los clientes menos el emisor
                if cliente[0] != id:         
                    cliente[1].send_bytes(data)
        
        except:     # Manejo de errores si un cliente se desconecta
            print('Se ha roto la conexión de audio con el cliente', id)
            enviando = False
    
    # Si el cliente se desconecta, se cierran las conexiones (se puede cerrar una conexión ya cerrada, no devuelve error)
    conn.close()
    conn_vid.close()
    conn_pzch.close()
    
    elim_conexion(id, lista_conexiones, semaforo_aud)     # Eliminamos al cliente de la lista de conexiones en la pizarra
    
    semaforo_i.acquire() # Añadimos una nueva id disponible
    if not id in i_disp:
        i_disp.append(id)
    semaforo_i.release()
            
def reenvio_video(conn, lista_conexiones, id, conn_pzch, conn_aud, i_disp, semaforo_i, semaforo_vid):
    enviando = True
    while enviando:
        try:
            long_vid = conn.recv_bytes(5) # Recibimos el tamaño del fotograma en 5 bytes 
            i = conn.recv_bytes(1) # Recibimos el ID del emisor del fotograma
            vid = conn.recv_bytes(int.from_bytes(long_vid, byteorder='big'))  # Recibimos tantos bytes como indique long_vid (pasándolo a entero) 
            
            for cliente in lista_conexiones:
                if (cliente[0] != id):
                    cliente[2].acquire() # Adquirimos el semáforo para enviar todos los comandos secuencialmente
                    cliente[1].send_bytes(long_vid)
                    cliente[1].send_bytes(i)
                    cliente[1].send_bytes(vid)
                    cliente[2].release()
        except: # Manejo de errores si un cliente se desconecta
            print('Se ha roto la conexión de video con el cliente', id)
            enviando = False

    # Si el cliente se desconecta, se cierran las conexiones (se puede cerrar una conexión ya cerrada, no devuelve error)    
    conn.close()
    conn_pzch.close()
    conn_aud.close()
    
    elim_conexion(id, lista_conexiones, semaforo_vid)     # Eliminamos al cliente de la lista de conexiones en la pizarra
    
    semaforo_i.acquire() # Añadimos una nueva id disponible
    if not id in i_disp:
        i_disp.append(id)
    semaforo_i.release()

if __name__ == '__main__':
    ip = '192.168.1.132'
    
    # Creamos un listener para cada función de la plataforma
    listener_vid = Listener(address=(ip, 8485), authkey=b'prueba')
    listener_aud = Listener(address=(ip, 8486), authkey=b'prueba')
    listener_pzch = Listener(address=(ip, 8487), authkey=b'prueba') 
    listener_bomb = Listener(address=(ip, 8488), authkey=b'prueba') 
    listener_pong = Listener(address=(ip, 8489), authkey=b'prueba') 
    
    # Preguntamos si el servidor es Windows o Ubuntu para las notifcaciones
    so = input('Introduce w si utilizas Windows o u Ubuntu: ')
    while so != 'u' and so != 'w':
        so = input('Introduce w si utilizas Windows o u Ubuntu: ')
    
    notificaciones = Notificaciones(False, so)    # Llamamos al modulo notificaciones para las notificaciones
    
    print('Empezando el listener...')
    
    manager = Manager()
    
    semaforo_i = manager.Lock()          # Semáforo para las ids de los clientes
    semaforo_aud = manager.Lock()        # Semáforo para el audio de los clientes
    semaforo_vid = manager.Lock()        # Semáforo para el video de los clientes
    semaforo_pzch = manager.Lock()       # Semáforo para la pizarra de los clientes
    lista_conexiones_vid = manager.list()  # Lista conexiones video
    lista_conexiones_aud = manager.list()  # Lista conexiones audio
    lista_conexiones_pzch = manager.list() # Lista conexiones pizarra
    i_disp = manager.list(range(8))

    Process(target=crear_entorno_bomberman, args=(listener_bomb, )).start()    # Iniciamos un proceso para jugar al Bomberman
    Process(target=crear_entorno_pong, args=(listener_pong, )).start()         # Iniciamos un proceso para jugar al Pong online

    while True:
        try:
            print('Esperando conexiones nuevas...')
            conn_vid = listener_vid.accept()         # Aceptamos la conexión de video del cliente
            conn_aud = listener_aud.accept()         # Aceptamos la conexión del audio del cliente
            conn_pzch = listener_pzch.accept()
            print('He aceptado una conexión de ', listener_vid.last_accepted)
            notificaciones.notificar(str(listener_vid.last_accepted), "Nueva conexión de ")   # Notificaciones emergentes de las conexiones de los suscriptores
            while len(i_disp) == 0:
                conn_vid.send("Se ha alcanzado el número máximo de jugadores. Espere por favor...")     # Mensaje para mantener a un clinte a la espera si se ha alcanzado el número máximo de clientes
                sleep(2)
            
            semaforo_i.acquire()
            i = i_disp.pop(0)       # Eliminamos al cliente que se desconecte de la lista de conexiones
            semaforo_i.release()
            
            print('Comunicando su id...')
            conn_vid.send_bytes((i).to_bytes(5, byteorder='big'))
            print('Hecho')
            
            l_video = manager.Lock()
            semaforo_vid.acquire()
            lista_conexiones_vid.append((i, conn_vid, l_video))
            semaforo_vid.release()
            semaforo_aud.acquire()
            lista_conexiones_aud.append((i, conn_aud))
            semaforo_aud.release()
            l_pzch = manager.Lock()
            semaforo_pzch.acquire()
            lista_conexiones_pzch.append((i, conn_pzch, l_pzch))
            semaforo_pzch.release()
            
            # Iniciamos procesos de reenvío de video, audio y pizarra
            print('Creando nuevos procesos para el cliente...')
            Process(target=reenvio_video, args=(conn_vid, lista_conexiones_vid, i, conn_pzch, conn_aud, i_disp, semaforo_i, semaforo_vid)).start()
            Process(target=reenvio_audio, args=(conn_aud, lista_conexiones_aud, i, conn_vid, conn_pzch, i_disp, semaforo_i, semaforo_aud)).start()
            Process(target=reenvio_pzch, args=(conn_pzch, lista_conexiones_pzch, i, conn_vid, conn_aud, i_disp, semaforo_i, semaforo_pzch)).start()
        except AuthenticationError:
            print ('Conexión rechazada: contraseña incorrecta')    # Manejo de errores por contraseña incorrecta

