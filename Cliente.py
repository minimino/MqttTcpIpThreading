from multiprocessing.connection import Client
from multiprocessing import Process, Queue, Manager
from audio_client import audio
from video_client import video
from pizarra_client import Minijuegos
from notificaciones import Notificaciones
from tkinter import *
from tkinter import messagebox, font
import sys

def iniciar_cliente(datos_cliente, entrada_usuario, entrada_ip, ventana):
    # Enviamos ventanas emergentes con información sobre avisos para el cliente si no ha rellenado todos los datos que se piden
    if datos_cliente[0] == '':
        messagebox.showinfo("¡Error!", "Tienes que seleccionar tu sistema operativo antes de iniciar")
    elif entrada_usuario.get() == '' or entrada_usuario.get() == "Introduce tu nombre o apodo: " or len(entrada_usuario.get()) > 25:
        messagebox.showinfo("¡Error!", "Tu nombre no puede ser vacío y tiene que ser distinto del texto inicial. Además, tiene que tener menos de 25 caracteres.")
    elif entrada_ip.get() == '' or entrada_ip.get() == "Introduce la IP del servidor: ":
        messagebox.showinfo("¡Error!", "La IP no es válida")
    else:
        # Quitamos espacios involuntarios al final o al inicio de la IP y del nombre
        datos_cliente[1] = entrada_usuario.get().strip()
        datos_cliente[2] = entrada_ip.get().strip()
        ventana.destroy()       # Eliminar la ventana inicial cuando se han rellenado todos los datos del usuario
    
def establecer_so(datos_cliente, so):
    datos_cliente[0] = so

def borrar_txt(texto, entrada):
    texto.set("")
    entrada.unbind("<Button 1>")

def crear_ventana_inicio(datos_cliente):
    # Ventana emergente
    ventana = Tk()   #Crear la ventana
    ventana.config(bg="pink")    # Color de fondo de la ventana
    ventana.geometry("622x360")    # Tamaño de la ventana
    ventana.resizable(width=FALSE, height=FALSE)   # Tamaño invariante de la ventana de menú
    ventana.title("Menu de selección de sistema operativo")    #Aparece en la parte superior de la ventana que se abre
    
    # Definimos dos botones para recibir notificaciones emergentes, uno para Windows y otro para Ubuntu
    Button(ventana, text="Ubuntu", width=20, height=10, bg = 'red', fg = 'white', command = lambda : establecer_so(datos_cliente, "u")).grid(column=1, row=2)
    Button(ventana, text="Windows", width=20, height=10, bg = 'blue', fg = 'white', command = lambda : establecer_so(datos_cliente, "w")).grid(column=4, row=2)
    
    # Creamos una etiqueta
    Label(ventana, bg="pink", fg="blue", width=27, height=10, text="Bienvenido a ParalelaParty   \n   :) \n Elige tu sistema operativo", font=("Arial", 12, "bold")).grid(column=3, row=2)
    
    # Definimos una entrada para la ipdel servidor al que se quiere conectar
    texto_ip = StringVar()
    texto_ip.set("Introduce la IP del servidor: ")
    entrada_ip = Entry(ventana, width=30, bg="white", fg="black", textvariable=texto_ip)
    entrada_ip.bind('<Button-1>', lambda e : borrar_txt(texto_ip, entrada_ip))
    
    # Definimos una entrada para el nombre del usuario
    texto_usuario = StringVar()
    texto_usuario.set("Introduce tu nombre o apodo: ")
    entrada_usuario = Entry(ventana, width=30, bg="white", fg="black", textvariable=texto_usuario)
    entrada_usuario.bind('<Return>', lambda e : iniciar_cliente(datos_cliente, entrada_usuario, entrada_ip, ventana))
    entrada_usuario.bind('<Button-1>', lambda e : borrar_txt(texto_usuario, entrada_usuario))
    entrada_ip.grid(column=3, row=3)
    entrada_usuario.grid(column=3, row=4, padx=10, pady=30)
    
    # Creamos botón para iniciar la plataforma una vez que se han rellenado los datos del usuario
    Button(ventana, text="Iniciar", width=10, height=2, bg = 'yellow', fg = 'black', command = lambda : iniciar_cliente(datos_cliente, entrada_usuario, entrada_ip, ventana)).grid(column=3, row=5)
    
    ventana.mainloop()

if __name__ == '__main__':
    # El primer elemento será el sistema operativo del cliente, el segundo el nombre y el tercero la ip del servidor
    datos_cliente = Manager().list(['', '', ''])
    inicio = Process(target=crear_ventana_inicio, args=(datos_cliente,))
    inicio.start()
    inicio.join()    # Garantizamos que acabe el proceso de rellenado de datos antes de iniciar la plataforma
    
    # Comprobamos si el usuario ha cerrado la ventana sin introducir los datos
    if ('' in datos_cliente):
        messagebox.showinfo("¡Error!", "No se han iniciado correctamente las varibales. Intenta abrir de nuevo el programa.")
        sys.exit()
    
    notificaciones = Notificaciones(True, datos_cliente[0])
    print(datos_cliente)
    # Llamamos a la clase notificaciones para recibir notificaciones emergentes del cliente y el chat
    print('Intentando conectarme al servidor...')

    cola_notifs = Queue()   # Cola donde, desde la pizarra vamos metiendo notificaciones, notificaciones que recibimos en el While True del final del código
    
    client_vid = Client(address=(datos_cliente[2], 8485), authkey=b'prueba')   # El cliente se conecta a la señal de video de la ip dada y el puerto 8485
    client_aud = Client(address=(datos_cliente[2], 8486), authkey=b'prueba')   # El cliente se conecta a la señal de audio de la ip dada y el puerto 8485
    client_pzch = Client(address=(datos_cliente[2], 8487), authkey=b'prueba')  # El cliente se conecta a la señal de pizarra y chat de la ip dada y el puerto 8485
    print('Conectado.')

    print('Recibiendo id...')
    id = int.from_bytes(client_vid.recv_bytes(5), byteorder='big')    # Para recibir elementos, tenemos que pasar lo que recibimos de bytes a int, para obtener la id
    print('Mi id es: ', id)
    
    print('Creando nuevos procesos para el cliente...')
    Process(target=video, args=(client_vid, id)).start()                 # Se crea un proceso para el video del cliente
    Process(target=audio, args=(client_aud,)).start()                    # Se crea un proceso para el audio del cliente
    Process(target=Minijuegos, args=(client_pzch, id, cola_notifs, datos_cliente[1], datos_cliente[2], datos_cliente[0])).start()    # Se crea un proceso para la pizarra del cliente. Se pasa como parámetro cola_notifs para recibir
                                                                         # notificaciones emergentes del chat
    
    while True:
        nombre, msj = cola_notifs.get(True)         # Bucle para recibir notificaciones emergentes del chat
        notificaciones.notificar(nombre, msj)

""" 
Como no podemos meter la clase notificaciones como parámetro, porque no es "pickable",
lo que hacemos es crear una cola para establecer una comunicacion entre el proceso 
principal y la clase notificaciones.
"""
