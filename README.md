# MqttTcpIpThreading
University assignment. The aim was to use TCP/IP protocol, MQTT communication, threading and multiprocessing with Python. My group (2 colleagues plus myself) decided to make a collaborative game center, where the users could make videocalls between them, share a whiteboard, chat, play Bomberman or even play Pong.


## Videocalls

The videocalls were implemented using TCP sockets through the *multiprocessing.connection* library. Roughly, the procedure was the following:
1. The clients captures a frame and some bytes of audio
2. This data is turned into bytes (using *numpy*'s *tobytes* method) and then compressed using (*zlib*)
3. The size of the result is calculated, and its communicated to the other users
4. The data is sent in packets of equal size to the other users
5. The other users unpack the data and show it on screen

Similar procedures were used for the other components (whiteboard, chat, Bomberman...), except that in those cases the packets had constant size, so step 3 is skipped. Of course, this needed a server which handled all communications between clients and allowed logging in.

## Pong

Although the aim of MQTT is not to broadcast games, we thought it was an original way of implementing it. The player of Pong would be the MQTT broker, and it would broadcast its moves to the suscribers, who could watch the game.
