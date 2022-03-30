# encoding: utf-8
from multiprocessing.connection import Client
from multiprocessing import Process
import cv2
from zlib import compress, decompress #libreria para comprimir los fotogramas aun mas
import numpy as np

class video():
    def __init__(self, conn, i): #la clase para ser iniciada recibe una conexion de un cliente y una id
        self.conn = conn 
        print('Iniciando envío de vídeo...')
        Process(target=self.envio_cam, args=(i,)).start() #inicia el proceso de la funcion de enviar la camara
        print('Iniciando recepción de vídeo...')
        self.recibir_cams() #inicia el proceso de la funcion recibir grabaciones

    def envio_cam(self, id): 
        cap = cv2.VideoCapture(0) #Activa la camara y empieza a grabar
        cap.set(3, 320)
        cap.set(4, 240)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20] #Determinamos la calidad de la grabacion en formato jpg con calidad 20 en una escala de 0-100
        
        print('Grabando vídeo...')

        while True:
            _, fotograma = cap.read() #Devuelve un booleano en función de si el frame se lee correctamente
            _, fotograma = cv2.imencode('.jpg', fotograma, encode_param) #Codificamos el fotograma en formato jpg
            
            a = fotograma.tobytes()
            datos = compress(fotograma.tobytes(), 1)        
            # print(len(datos)/len(a)) #vemos como hemos comprimido el tamaño del fotograma en este porcentaje
            
            self.conn.send_bytes((len(datos)).to_bytes(5, byteorder='big'))
            self.conn.send_bytes((id).to_bytes(1, byteorder='big')) #Enviamos la id al resto de usuarios
            self.conn.send_bytes(datos) #Enviamos el fotograma al resto de usuarios
            
            fotograma = cv2.imdecode(fotograma, cv2.IMREAD_COLOR) #lee la imagen del buffer
            cv2.imshow('Tú', fotograma) # muestra la imagen en la ventana del usuario
            cv2.waitKey(1)

    def recibir_cams(self): #funcion que recibe las grabaciones del resto de usuarios
        while True:
            long_vid = int.from_bytes(self.conn.recv_bytes(5), byteorder='big') 
            # print(long_vid) 
            i = int.from_bytes(self.conn.recv_bytes(1), byteorder='big') #recibe la id del usuario

            video = self.conn.recv_bytes(long_vid) 
            video = decompress(video)  #descomprime el video (esto es por la linea 29) del codigo
            video2 = np.frombuffer(video, dtype='uint8') #interpreta el buffer como un array
            video2 = video2.reshape(len(video2), 1) #tranforma el array en una lista de orden 1
            
            fotograma = cv2.imdecode(video2, cv2.IMREAD_COLOR) #lee la imagen del buffer
            cv2.imshow('Cámara ' + str(i), fotograma) #muestra la camara al resto de usuarios
            cv2.waitKey(1)
    