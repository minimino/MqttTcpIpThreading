class Notificaciones():   # Creamos la clase de notificaciones para crear notificaciones emergentes tanto en Windows como en Ubuntu
    def __init__(self, es_cliente, so):
        self.es_cliente = es_cliente     # Variable booleana. Si eres es_cliente = cliente, es True y si eres es_cliente = servidor
        self.so = so   # Preguntamos el sistema operativo para ver si es Windows o Ubuntu
            
        if es_cliente:
            self.texto_cliente = "CLIENTE"  # Si te conectas como cliente entonces aparecerá CLIENTE como etiqueta en la notificación
        else:
            self.texto_cliente = "SERVIDOR" # Si te conectas como servidor entonces aparecerá SERVIDOR como etiqueta en la notificación
        
        if self.so == 'w':    # Si eres Windows entonces importas la función ToastNotifier de la librería win10toast correspondiente a las notificaciones en Windows
            from win10toast import ToastNotifier   # Librería necesaria para activar las notificaciones en windows
            
            self.toaster = ToastNotifier()
            self.toaster.show_toast(self.texto_cliente, "Te has conectado como " + self.texto_cliente) # Manda la notificación con la etiqueta self.texto_cliente el texto "Te has conectado como self.texto_cliente"
        else:     # En caso contrario utilizas el sistema Ubuntu
            import notify2     # Importas la librería notify2 correspondiente a las notificaciones en Ubuntu
            
            notify2.init(self.texto_cliente)
            notificacion = notify2.Notification(self.texto_cliente, "Te has conectado como " + self.texto_cliente)
            notificacion.show() # Manda la notificación con la etiqueta self.texto_cliente  el texto "Te has conectado como self.texto_cliente"

    def notificar(self, user, msg):   # Función usada recibir notificaciones emergentes cuando se escribe un mensaje en el chat(solo se reciben notificaciones de los mensajes de otros usuarios)
        
        # Distinguimos entre las notificaciones del servidor y las del cliente
        if self.es_cliente:
            cabecera = "Chat"
            texto = str(user) + ": " + msg   # El texto de la notificación será " NombreUsuario: mensaje enviado por dicho usuario"
        else:
            cabecera = "Conexión nueva"
            texto = msg + user
        
        if self.so == 'w':
            self.toaster.show_toast(cabecera, texto)  # Recibir notificaciones emergentes del chat si eres Windows
        else:
            import notify2
            
            notify2.Notification(cabecera, texto).show()    # Notificaciones emergentes en el chat si eres Ubuntu

"""

IMPORTANTE: Debes descargarte la librería win10toast si tu sistema operativo es Windows o descargarte la librería notify2 si es Ubuntu.

Clase creada para recibir notificaciones emergentes tanto en Windows como en Ubuntu. Recibes dos tipos de notificaciones:
    - La primera notificación es diferente en función de si te has conectado como cliente o como servidor. Si eres cliente, 
      recibes como mensaje "Te has conectado como cliente". Por el contrario, si eres servidor recibes "te has conectado como servidor"
    
    - Las siguientes notificaciones son todas referentes al chat anexo a la pizarra. Solo las recibes si el usuario que las escribe es otro.
      El texto de la notificación será " NombreUsuario: mensaje enviado por dicho usuario"

"""