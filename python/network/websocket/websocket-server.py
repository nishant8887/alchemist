#!/usr/bin/env python
import os
import sys
import socket
import datetime
import base64
import hashlib

from threading import Thread

BUFFER_SIZE = 1024

ERROR_TCP_CONNECTION = 0
ERROR_TCP_DISCONNECTION = 1
ERROR_TCP_SEND = 2
ERROR_WEBSOCKET_HANDSHAKE_REQUEST = 3
ERROR_WEBSOCKET_RESPONSE_TOO_LONG = 4
ERROR_DECODING_RESPONSE = 5

class Server_Client(Thread):
    def __init__(self, server, socket, address):
        self.server = server
        self.socket = socket
        self.address = address
        self.protocol = None
        self.tcp_status = True
        self.ws_status = False
        super(Server_Client, self).__init__()

    def log(self, message):
        #print message
        sys.stderr.write(message+'\r\n')

    def onservermessage(self, message, msg_type):
        self.log("Message from server ...")
        self.send(message, msg_type)
    
    def onmessage(self, message, msg_type):
        self.log(message)
        self.sendall(message, msg_type)
        self.log("Message received ...")

    def onopen(self):
        self.log("Connection opened ...")

    def onclose(self):
        self.log("Connection closed ...")

    def onerror(self, error_type):
        self.log("Error occured [TYPE=" + str(error_type) + "] ...")
    
    def ping(self):
        if self.ws_status:
            data = "\x89\x00"
            self.tcp_send(data)

    def pong(self):
        if self.ws_status:
            data = "\x8A\x00"
            self.tcp_send(data)

    def close(self):
        if self.ws_status:
            data = "\x88\x00"
            self.tcp_send(data)

    def send(self, message, msg_type):
        if message and self.ws_status:
            data = self.convert_data(message, msg_type)
            self.tcp_send(data)

    def sendall(self, message, msg_type):
        self.server.sendall(message, msg_type, self)
    
    def onrequest(self, data):
        try:
            if self.ws_status:
                opcode = ord(data[0]) & 15
                #print "Opcode: " + str(opcode)
                
                if (ord(data[1]) < 128) or (opcode == 8):
                    self.close()
                    self.disconnect()
                    return
                
                if opcode == 1:
                    self.onmessage(self.parse_data(data), "text")
                elif opcode == 2:
                    self.onmessage(self.parse_data(data), "binary")
                elif opcode == 9:
                    self.pong()
                elif opcode == 10:
                    self.onmessage("Pong packet received ...", "text")
            else:
                request_dictionary = dict()
                request_header = data.split("\r\n\r\n")[0].split("\r\n")
                
                http_request_line = request_header[0].split()
                http_method = http_request_line[0]
                http_path = http_request_line[1]
                http_tag = http_request_line[2]
                
                http_name = http_tag.split("/")[0]
                http_version = float(http_tag.split("/")[1])
                
                status = False
                if (http_method.lower() == "get") and (http_name.lower() == "http") and (http_version >= 1.1):
                    status = True
                
                if not status:
                    self.log("No/Improper request line in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                '''
                status = False
                if(http_path == "/"):
                    status = True
                
                if not status:
                    self.log("No/Improper request path in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                '''
                
                ''' Other header fields '''
                
                for header in request_header[1:]:
                    parameter = header.split(":")[0].strip().lower()
                    value = "".join(header.split(":")[1:]).strip()
                    request_dictionary[parameter] = value
                
                status = False
                if "host" in request_dictionary:
                    #if request_dictionary["host"] == valid_url:
                    status = True
                
                if not status:
                    self.log("No/Improper host field in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                status = False
                if "connection" in request_dictionary:
                    if request_dictionary["connection"].lower() == "upgrade":
                        status = True
                
                if not status:
                    self.log("No/Improper connection field in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                status = False
                if "upgrade" in request_dictionary:
                    if request_dictionary["upgrade"].lower() == "websocket":
                        status = True
                
                if not status:
                    self.log("No/Improper upgrade field in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                '''
                status = False
                if "origin" in request_dictionary:
                    #if request_dictionary["origin"] == valid_url:
                    status = True
                
                if not status:
                    self.log("No/Improper origin field in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                '''
                
                status = False
                if "sec-websocket-key" in request_dictionary:
                    if len(request_dictionary["sec-websocket-key"]) == 24:
                        sha_key = request_dictionary["sec-websocket-key"]
                        self.key = base64.b64encode(hashlib.sha1(sha_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
                        status = True
                
                if not status:
                    self.log("No/Improper sec-websocket-key field in request ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                status = False
                if "sec-websocket-version" in request_dictionary:
                    if int(request_dictionary["sec-websocket-version"]) == 13:
                        status = True
                
                if not status:
                    self.log("No/Improper version used for connect ...")
                    self.disconnect()
                    self.onerror(ERROR_WEBSOCKET_HANDSHAKE_REQUEST)
                    return
                
                ''' Only one protocol to be sent not a preference list '''
                if "sec-websocket-protocol" in request_dictionary:
                    if request_dictionary["sec-websocket-protocol"] in self.server.protocols:
                        self.protocol = request_dictionary["sec-websocket-protocol"]
                
                self.log("Websocket handshake request successful ...")
                self.ws_status = True
                self.connect()
                self.onopen()
        except:
            self.log("Error decoding response ...")
            self.onerror(ERROR_DECODING_RESPONSE)

    def connect(self):
        self.log("Completing websocket handshake ...")
        message = 'HTTP/1.1 101 Web Socket Protocol Handshake\r\n'
        message += 'Server: Python Websocket\r\n'
        now = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        message += 'Date: '+ now +'\r\n'
        message += 'Connection: Upgrade\r\n'
        message += 'Upgrade: websocket\r\n'
        if self.protocol:
            message += 'Sec-WebSocket-Protocol: '+ self.protocol +'\r\n'
        message += 'Sec-WebSocket-Accept: '+ self.key +'\r\n\r\n'
        self.tcp_send(message)

    def run(self):
        self.log("Started thread for client " + str(self.address))
        while True:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    self.socket.close()
                    self.log("Connection closed from client ...")
                    raise Exception()
                self.onrequest(data)
            except:
                self.tcp_status = False
                self.log("Connection closed at TCP level ...")
                self.server.client_thread_closed(self)
                break

    def tcp_send(self, data):
        try:
            self.socket.sendall(data)
        except:
            self.log("Cannot send tcp data ...")
            self.onerror(ERROR_TCP_SEND)

    def disconnect(self):
        if self.tcp_status:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except:
                pass
                self.onerror(ERROR_TCP_DISCONNECTION)

    def parse_data(self, data):
        payload_length_byte_1 = ord(data[1]) & 127
        
        if payload_length_byte_1 < 126:
            payload_length = payload_length_byte_1
            masking_key = data[2:6]
            masked_message = data[6:]
        elif payload_length_byte_1 == 126:
            payload_length = int((data[2:4]).encode("hex"),16)
            masking_key = data[4:8]
            masked_message = data[8:]
        elif payload_length_byte_1 == 127:
            payload_length = int((data[2:10]).encode("hex"),16)
            masking_key = data[10:14]
            masked_message = data[14:]
        else:
            message = ""
            self.log("Response too long ...")
            self.onerror(ERROR_WEBSOCKET_RESPONSE_TOO_LONG)
            return message

        #print "Payload Length: " + str(payload_length)
        message = self.xor_hex_strings(masked_message, masking_key)
        return message

    def convert_data(self, message, msg_type):
        ''' Initial byte indicating that this is the only websocket frame for the message and having text data '''
        if msg_type == "text":
            data = "\x81"
        else:
            data = "\x82"
            
        ''' Define Payload Length section '''
        payload_length = len(message)
        payload_length_other_bytes = ""

        if payload_length < 126:
            payload_length_byte_1 = chr(payload_length)
        elif payload_length < 65536:
            payload_length_byte_1 = chr(126)
            for i in range(0,2):
                payload_length_other_bytes = chr(payload_length % 256) + payload_length_other_bytes
                payload_length = payload_length >> 8
        elif payload_length < pow(2,64):
            payload_length_byte_1 = chr(127)
            for i in range(0,8):
                payload_length_other_bytes = chr(payload_length % 256) + payload_length_other_bytes
                payload_length = payload_length >> 8
        else:
            data = "\x88\x00"	# Close connection if length exceeds pow(2,64)-1
            return data

        ''' Merge Payload Length section and Masking Key '''
        binary_payload_length = payload_length_byte_1 + payload_length_other_bytes

        data += binary_payload_length
        data += message
        return data

    def xor_hex_strings(self, xstr, ystr):
        xorstr = ""
        i = 0
        for x in xstr:
            y = ystr[i%len(ystr)]
            xorstr += chr(ord(x) ^ ord(y))
            i += 1
        return xorstr

class Server(Thread):
    def __init__(self, address, port, protocols):
        self.ipaddress = address
        self.client_list = []
        self.status = False
        self.port = port
        self.protocols = protocols
        super(Server, self).__init__()
    
    def log(self, message):
        #print message
        sys.stderr.write(message+'\r\n')

    def run(self):
        while True:
            try:
                (client_socket, address) = self.socket.accept()
                self.log("Connection request from " + str(address))
                client_thread = Server_Client(self, client_socket, address)
                client_thread.start()
                self.client_list.append(client_thread)
            except:
                self.status = False
                break

    def client_thread_closed(self, client_thread):
        self.client_list.remove(client_thread)
    
    def sendall(self, message, msg_type, sender=None, protocol=None):
        if sender:
            for client in self.client_list:
                if (client != sender) and (client.protocol == sender.protocol):
                    client.onservermessage(message, msg_type)
        else:
            for client in self.client_list:
                if client.protocol == protocol:
                    client.onservermessage(message, msg_type)

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ipaddress, self.port))
        self.socket.listen(5)
        self.status = True
        self.start()
    
    def stop_server(self):
        if self.status:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
                for client in self.client_list:
                    client.disconnect()
            except:
                pass

HOST = os.environ.get("OPENSHIFT_DIY_IP")
if not HOST:
    HOST = '127.0.0.1'

PORT = 8080
sys.stderr.write('Starting up server ...\n')
tcpserver = Server(HOST, PORT,[])
tcpserver.start_server()
