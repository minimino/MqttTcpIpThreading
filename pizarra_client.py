from multiprocessing.connection import Client
from threading import Thread, Timer
import pickle
from tkinter import *
from tkinter import ttk, colorchooser, messagebox
import tkinter.font as tkFont
from datetime import datetime
from tablero import Tablero
from pong import Pong
from pong_offline import Pong_offline
from rompeladrillos import Rompeladrillos

class Minijuegos:
    def __init__(self, conn, id, cola_notifs, mi_nombre, ip_servidor, so):
        # Creamos la ventana principal de la pizarra, chat y menú de juegos
        self.master = Tk()
        self.master.resizable(False, False)    # Evitamos que la ventana pueda variar de tamaño
        self.master.title('ParalelaParty')     # Titulo de la ventana
        self.cola_notifs = cola_notifs         # Cola de notificaciones para el chat
        self.mi_nombre = mi_nombre
        self.ip_servidor = ip_servidor
        self.id = id
        self.so = so
        self.conn = conn
        self.colores = ['black', 'red', 'blue', 'green', 'yellow', 'pink', 'orange']    # Distinto color para cada usuario
        
        # Pizarra
        self.color_fg = 'black'
        self.color_bg = 'white'    # Fondo de la pizarra
        self.old_x = None
        self.old_y = None
        self.penwidth = 5          # Anchura pincel
        print("Creando canvas...")
        self.c = Canvas(self.master, width=400, height=400, bg=self.color_bg)     # Creación de la pizarra dentro de la ventana principal
        self.c.bind('<B1-Motion>', self.paint_local)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.jugando_bomberman = False
        self.jugando_pong = False
        self.jugando_rlad = False
        
        Thread(target=self.act_canvas).start()      # Actualizar el canvas. Con el multiprocessing no se pueden pasar objetos de tkinter
        
        self.controls = Frame(self.master) #Creamos un marco para el Regulador
        self.controls.grid_columnconfigure(2, weight=1)
        self.controls.grid_rowconfigure(2, weight=1)
        self.slider = ttk.Scale(self.controls, from_= 5, to = 100, command=self.changeW, orient=VERTICAL) #Crea una escala, y le agrgamos command changeW
        self.slider.set(self.penwidth)
        #Creamos la Barra de Menu
        menu = Menu(self.master) #Creamos una barra de menu 
        self.master.config(menu=menu)
        #filemenu = Menu(menu) 
        colormenu = Menu(menu) # Agregar menu a la barra de menu
        menu.add_cascade(label='Colores',menu=colormenu) #añadir etiqueta al menu indicado y crear cascada de submenus
        colormenu.add_command(label='Color del pincel',command=self.change_fg) #añadir etiqueta a cada uno de los submenus
        colormenu.add_command(label='Color del fondo',command=self.change_bg)
        optionmenu = Menu(menu)
        menu.add_cascade(label='Opciones',menu=optionmenu)
        optionmenu.add_command(label='Borrar pizarra',command=self.clear)
        
        # Creamos menú de juegos
        juegosmenu = Menu(menu)
        menu.add_cascade(label='Juegos',menu=juegosmenu)    # Barra adicional para introducir los juegos
        # Botones juegos
        juegosmenu.add_command(label='Jugar al Bomberman',command=self.emp_bomberman)
        juegosmenu.add_command(label='Jugar al Pong',command=self.emp_pong)
        juegosmenu.add_command(label= 'Jugar al Pong offline', command=self.emp_pong_offline)
        juegosmenu.add_command(label='Jugar al RompeLadrillos',command=self.emp_rlad)
        
        # Chat
        self.marco_msjs = Frame(self.master)    # Meter el chat en la ventana principal
        self.entrada_txt = StringVar()          # Barra para escribir en el chat
        self.entrada_txt.set("Escribe tu mensaje: ")   # Mensaje inicial de la barra de chat
        self.barra = Scrollbar(self.marco_msjs)
        self.lista_msjs = Text(self.marco_msjs, width=40, yscrollcommand=self.barra.set)  # Aparecen los mensajes en la ventana del chat
        self.entrada = Entry(self.marco_msjs, width=40, textvariable=self.entrada_txt)
        self.entrada.bind('<Return>', self.env_chat)   # Enviar mensajes al chat pulsando la tecla enter
        self.env_btn = Button(self.marco_msjs, text="Enviar", bg = 'green', fg = 'white', command = self.env_chat)   # Botón para enviar mensajes
        self.clickado = False
        self.entrada.bind('<Button-1>', self.borrar_txt)
        
        # Emoticonos
        # Lista emoticonos
        self.lista_emoticonos = [ "\ud83d\ude4f", "\uD83E\uDD14", "\uD83D\uDE04", "\uD83D\uDE01", "\uD83E\uDD23", "\uD83D\uDE02", "\uD83D\uDE43", "\uD83D\uDE09", "\uD83E\uDD29", "\uD83D\uDE18", "\uD83E\uDD2A", "\uD83D\uDE0B", "\uD83E\uDD14", "\uD83E\uDD10", "\uD83D\uDE2A", "\uD83E\uDD22" ] 
        
        for (ind, cod) in zip(range(len(self.lista_emoticonos)), self.lista_emoticonos):   # Bucle de botones para todos los emoticonos
            Button(self.controls, text=cod, bg = 'white', fg = 'black', command = lambda ind=ind: self.env_emoji(ind)).grid(column=ind%4, row=3+ind//4)
        
        # Posiciones de los distintos elementos del chat y deslizador
        self.c.grid(column=0, row=0, rowspan=5, sticky=W+N+S+E)      # Posiciones botones emoticonos con el comando grid
        self.marco_msjs.grid(column=1, row=0, rowspan=5, sticky=W+N+S+E)
        self.controls.grid(column=2, row=0, rowspan=5, sticky=W+N+S+E)
        self.lista_msjs.grid(row=0, column=0, rowspan=4, sticky=W+N+S)  # Posición donde aparecen la lista de mensajes en chat
        self.barra.grid(row=0, column=1,rowspan=4, sticky=E+N+S)
        self.entrada.grid(row=4, sticky=W+S+N)
        self.env_btn.grid(row=4, columnspan=2,sticky=E+S+N)
        self.slider.grid(row=1, column=0, columnspan=4, sticky=N+E+S+W) # Posición deslizador
        Label(self.controls, text='Grosor:',font=('arial 10')).grid(row=0, column=0, columnspan=4, sticky=N+E+S+W)
        self.master.mainloop()
      
    # Función para iniciar juego del bomberman
    def emp_rlad(self):
        if not self.jugando_rlad:
            self.conn.send_bytes((0).to_bytes(10, byteorder='big'))
            self.jugando_rlad = True # Así evitamos que el usuario se conecte varias veces al servidor        
    
    # Función para iniciar juego del bomberman
    def emp_bomberman(self):
        if not self.jugando_bomberman:
            Thread(target=self.conectar_bomberman).start()   # Thread nuevo para conectarse al bomberman
            self.jugando_bomberman = True # Así evitamos que el usuario se conecte varias veces al servidor
            
    def conectar_bomberman(self):
        client_bomb = Client(address=(self.ip_servidor, 8488), authkey=b'prueba') # Nos conectamos al servidor
        datos = pickle.dumps("{:<25}".format(self.mi_nombre)) # Pasamos a 35 bytes nuestro nombre
        client_bomb.send_bytes(datos) # Enviamos nuestro nombre
        self.env_notif_serv(self.mi_nombre + " está buscando compañeros para echar una partida de bomberman") # Ponemos en el chat un mensaje diciendo que el cliente busca compañeros para jugar
        b = Button(self.controls, text="Listo para jugar", bg = 'green', fg = 'white', command = lambda : self.btn_listo(b, client_bomb)) # Crea el botón "Listo para jugar"
        b.grid(row=2, column=0, columnspan=4)
        los_cacharritos = client_bomb.recv() # Recibimos los datos del tablero del servidor
        
        if los_cacharritos[-1] == 1:
            texto = ""
            for nombre, m in los_cacharritos[3]:
                if m == los_cacharritos[3][-1][1]: # Si es la última persona de la lista...
                    if los_cacharritos[2] > 1:
                        # Va a jugar más de una persona
                        texto += " y " + nombre + " van a jugar al bomberman"
                    else:
                        # Va a jugar una persona
                        texto += nombre + " va a jugar al bomberman"
                elif m == los_cacharritos[3][0][1]: # Si es la primera persona de la lista...
                    texto += nombre
                else:
                    texto += ", " + nombre
            
            self.env_notif_serv(texto) # Notificamos en el chat que se va a empezar una partida de bomberman
        
        Tablero(los_cacharritos[0], los_cacharritos[1], los_cacharritos[2], los_cacharritos[3], self.mi_nombre, client_bomb, self.master) # Iniciamos el bomberman
    
    def emp_pong(self):
        if not self.jugando_pong:
            Thread(target=self.conectar_pong).start()     # Thread nuevo para conectarse al pong
            self.jugando_pong = True # Así evitamos que el usuario se conecte varias veces al servidor
            
    def conectar_pong(self):
        client_pong = Client(address=(self.ip_servidor, 8489), authkey=b'prueba') # Nos conectamos al servidor
        self.env_notif_serv(self.mi_nombre + " está buscando compañeros para echar una partida de pong") # Ponemos en el chat un mensaje diciendo que el cliente busca compañeros para jugar
        id = int.from_bytes(client_pong.recv_bytes(1), byteorder='big') # Recibimos nuestra id del servidor
        datos = pickle.dumps("{:<25}".format(self.mi_nombre)) # Pasamos a 35 bytes nuestro nombre
        b = Button(self.controls, text="Listo para jugar", bg = 'green', fg = 'white', command = lambda : self.btn_listo(b, client_pong, datos)) # Crea el botón "Listo para jugar"
        b.grid(row=2, column=0, columnspan=4)
        nombre_oponente = pickle.loads(client_pong.recv_bytes(35)).strip() # Recibimos el nombre del oponente y le quitamos los posibles caracteres añadidos
        
        if id == 0:
            self.env_notif_serv(self.mi_nombre + " y " + nombre_oponente + "van a empezar una partida de pong") # Notificamos en el chat que se va a empezar una partida de pong online
        
        try:
            Pong(client_pong, id, self.mi_nombre, nombre_oponente)
        except:
            client_pong.close()
    
    # Función para iniciar pong offline
    def emp_pong_offline(self):
        # Imprimimos los controles del pong offline en el chat
        LineNumber = float(self.lista_msjs.index('end'))-1.0
        self.lista_msjs.insert(END, "Jugador1(CONTROLES): Flecha arriba para mover la raqueta hacia arriba y flecha abajo para mover raqueta hacia abajo \n")
        self.lista_msjs.tag_add("Jugador1(CONTROLES)", LineNumber, LineNumber+0.117)
        self.lista_msjs.tag_config("Jugador1(CONTROLES)", foreground='blue', font=("Arial", 12, "bold"))
        LineNumber = float(self.lista_msjs.index('end'))-1.0
        self.lista_msjs.insert(END, "Jugador2(CONTROLES): 'w' para mover la raqueta hacia arriba y 's' para mover raqueta hacia abajo \n")
        self.lista_msjs.tag_add("Jugador2(CONTROLES)", LineNumber, LineNumber+0.96)
        self.lista_msjs.tag_config("Jugador2(CONTROLES)", foreground='magenta', font=("Arial", 12, "bold"))
        try:
            Pong_offline()     # Llamamos a la clase Pong_offline del archivo pong_offline
        except:
            pass
    
    # Función para mandar mensajes sobre el estado de los juegos a través de la ventana de chat  
    def env_notif_serv(self, msj):
        msj_byn = pickle.dumps((0, msj+'\n', "Servidor", -1))
        
        LineNumber = float(self.lista_msjs.index('end'))-1.0
        self.lista_msjs.insert(END,"Servidor: "+ msj+'\n')
        self.lista_msjs.tag_add("Servidor", LineNumber, LineNumber+0.9)
        self.lista_msjs.tag_config("Servidor", foreground=self.colores[-1], font=("Arial", 12, "bold"))
        self.conn.send_bytes(len(msj_byn).to_bytes(10, byteorder='big'))
        self.conn.send_bytes(msj_byn)
        self.entrada.delete(first=0, last=100)
    
    # Botón para confirmar que se está listo para jugar a un juego
    def btn_listo(self, boton, conn, datos = (1).to_bytes(1, byteorder='big')):
        conn.send_bytes(datos)
        boton.grid_remove()
        
    def act_canvas(self):
        print("Esperando cambios en el canvas y chat...")
        while True:
            longitud_msj = int.from_bytes(self.conn.recv_bytes(10), byteorder='big')
            com = pickle.loads(self.conn.recv_bytes(longitud_msj))
            if com[0] == 1:
                self.c.create_line(com[1], com[2], com[3], com[4], width=com[5], fill= com[6], capstyle=ROUND, smooth=True)  # Crear líneas para pintar en pizarra
            elif com[0] == 2:
                self.c['bg'] = com[1]    # Cambiar color fondo
            elif com[0] == 3:
                self.c.delete(ALL)   # Borrar pizarra
            elif com[0] == 0:
                LineNumber = float(self.lista_msjs.index('end'))-1.0
                self.lista_msjs.insert(END, com[2] + ": " + com[1])
                self.lista_msjs.tag_add(com[2], LineNumber, LineNumber+(len(com[2]) + 1)/10)
                self.lista_msjs.tag_config(com[2], foreground = self.colores[com[3]], font=("Arial", 12, "bold"))
                if self.so != 'u' or (com[1].rstrip("\n") not in self.lista_emoticonos):
                    self.cola_notifs.put((com[2], com[1])) # Añadimos el nuevo mensaje al chat
            else:
                # Queremos ver/jugar al rompeladrillos
                if com[1] > 0: # Espectador
                    b = Button(self.controls, text="Ver la partida", bg = 'green', fg = 'white', command = lambda i = com[2] : self.ver_rlad(b, i)) # Crea el botón "Ver la partida"
                    b.grid(row=2, column=0, columnspan=4)
                    Timer((com[2] - datetime.now()).total_seconds(), lambda : b.grid_remove()).start() # Destruimos el botón a los 15 segundos
                else: # Jugador
                    self.env_notif_serv(self.mi_nombre + " va a jugar una partida de rompeladrillos en menos de 15 segundos. Haz click en 'Ver la partida' para verla.") # Notificamos en el chat que se va a empezar una partida de rompeladrillos
                    retraso = (com[2] - datetime.now()).total_seconds()
                    Timer(retraso, Rompeladrillos, [False, self.master]).start() # Empezamos el rompeladrillos a los 15 segundos

    def ver_rlad(self, boton, hora):
        retraso = (hora - datetime.now()).total_seconds() # Calculamos cuánto queda para que se inicie el juego
        Timer(retraso, Rompeladrillos, [True, self.master]).start() # Empezamos el rompeladrillos al transcurrir retraso segundos
        boton.grid_remove() # Eliminamos el botón 'Ver la partida'
    
    # Borrar texto de la barra de chat al clickar
    def borrar_txt(self, e):
        if not self.clickado:
            self.entrada_txt.set("")
            self.clickado = True
    
    # Enviar mensajes al chat
    def env_chat(self, e = None):
        msj = self.entrada.get()+'\n'
        msj_byn = pickle.dumps((0, msj, self.mi_nombre, self.id))
        
        if (len(msj_byn) > 1e+23):   # Solo admite mensajes de hasta una cierta longitud
            messagebox.showinfo("¡Error!", "Estás intentando enviar un mensaje demasiado largo")
        else:
            LineNumber = float(self.lista_msjs.index('end'))-1.0
            self.lista_msjs.insert(END,"Tú: "+ msj)   # Insertamos el mensaje en el chat para que lo puedan ver el resto de usuarios
            self.lista_msjs.tag_add("Tú", LineNumber, LineNumber+0.4)
            self.lista_msjs.tag_config("Tú", foreground=self.colores[self.id], font=("Arial", 12, "bold")) # Los mensajes aparecerán en el fondo con esa fuente de letra
            self.conn.send_bytes(len(msj_byn).to_bytes(10, byteorder='big'))
            self.conn.send_bytes(msj_byn)
            self.entrada.delete(first=0, last=100)
    
    def env_emoji(self, numero, e = None):
        emoticono = self.lista_emoticonos[numero]+'\n'    # Accedemos a la lista de emoticonos
        LineNumber = float(self.lista_msjs.index('end'))-1.0
        self.lista_msjs.insert(END,"Tú: " + emoticono)# Insertamos el emoticono en el chat para que lo puedan ver el resto de usuarios
        self.lista_msjs.tag_add("Tú", LineNumber, LineNumber+0.4)
        self.lista_msjs.tag_config("Tú", foreground=self.colores[self.id], font=("Arial", 12, "bold"))   # Los mensajes aparecerán en el fondo con esa fuente de letra
        com = (0, emoticono, self.mi_nombre, self.id)
        data = pickle.dumps(com)
        self.conn.send_bytes(len(data).to_bytes(10, byteorder='big'))
        self.conn.send_bytes(data)
     
    def paint_local(self, e):
        if self.old_x and self.old_y:
            com = (1, self.old_x, self.old_y, e.x, e.y, self.penwidth, self.color_fg)
            self.c.create_line(com[1], com[2], com[3], com[4], width=self.penwidth, fill=self.color_fg, capstyle=ROUND, smooth=True)
            data = pickle.dumps(com)
            self.conn.send_bytes(len(data).to_bytes(10, byteorder='big'))
            self.conn.send_bytes(data)
            
        self.old_x = e.x
        self.old_y = e.y
    
    def reset(self, e):
        self.old_x = None
        self.old_y = None
    
    # Borrar la pizarra
    def clear(self):
        self.c.delete(ALL)
        com = (3, "Delete All")
        data = pickle.dumps(com)
        self.conn.send_bytes(len(data).to_bytes(10, byteorder='big'))
        self.conn.send_bytes(data)
    
    # Cambiar color de pincel
    def change_fg(self):
        self.color_fg=colorchooser.askcolor(color=self.color_fg)[1]
    
    # Cambiar color fondo pizarra
    def change_bg(self):
        self.color_bg=colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg
        com = (2, self.color_bg)
        data = pickle.dumps(com)
        self.conn.send_bytes(len(data).to_bytes(10, byteorder='big'))
        self.conn.send_bytes(data)
    
    # Cambiar el tamaño el pendwidth
    def changeW(self,e):
        self.penwidth = e
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        