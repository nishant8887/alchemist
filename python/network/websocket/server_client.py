import websocket
import json
import random

class MyWsClient(websocket.WebSocketClient):
    def __init__(self, server, port, protocols):
        super(MyWsClient, self).__init__(server, port, protocols, True)
    
    def onopen(self):
        print "Connection opened ..."
    
    def onclose(self):
        print "Connection closed ..."
    
    def onmessage(self, message, msg_type):
        print message
    
    def onerror(self, error_type):
        print error_type
    
    def send_message(self, message):
        self.send(message, "text")

TCP_IP = 'echo.websocket.org'
TCP_PORT = 80

#TCP_IP = 'websocket-nishantns.rhcloud.com'
#TCP_PORT = 8000

#TCP_IP = 'localhost'
#TCP_PORT = 8080

tcpclient = MyWsClient(TCP_IP, TCP_PORT, [])
tcpclient.open()

while True:
    line = raw_input()
    line_stream = line.split()
    cmd = line_stream[0]
    arg = " ".join(line_stream[1:])
    
    if cmd == "":
        tcpclient.close()
        break
    elif cmd == "ping":
        tcpclient.ping()
    elif cmd == "msg":
        tcpclient.send_message(arg)
