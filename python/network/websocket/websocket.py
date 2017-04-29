#!/usr/bin/env python
import socket
import random
import base64
import sha

from threading import Thread
from time import sleep

BUFFER_SIZE = 1024

ERROR_TCP_CONNECTION = 0
ERROR_TCP_DISCONNECTION = 1
ERROR_TCP_SEND = 2
ERROR_WEBSOCKET_HANDSHAKE = 3
ERROR_WEBSOCKET_HANDSHAKE_RESPONSE = 4
ERROR_WEBSOCKET_RESPONSE_TOO_LONG = 5
ERROR_DECODING_RESPONSE = 6

class WebSocketClient(Thread):
	def __init__(self, server, port, protocols, debug=False):
		self.server = server
		self.port = port
		self.protocols = protocols
		self.debug = debug
		self.ws_status = False
		self.tcp_status = False
		self.ws_framedata = ''
		super(WebSocketClient, self).__init__()

	def run(self):
		while True:
			try:
				data = self.socket.recv(BUFFER_SIZE)
				if not data:
					self.socket.close()
					raise Exception()
				self.onresponse(data)
			except:
				self.ws_status = False
				self.tcp_status = False
				self.log("Connection closed at TCP level ...")
				self.onclose()
				break

	def onmessage(self, message, msg_type):
		self.log("Message received ...")

	def onopen(self):
		self.log("Connection opened ...")
	
	def onclose(self):
		self.log("Connection closed ...")
	
	def onerror(self, error_type):
		self.log("Error occured [TYPE=" + str(error_type) + "] ...")
	
	def log(self, message):
		if self.debug:
			print message

	def send(self, message, msg_type):
		if message and self.ws_status:
			data = self.convert_data(message, msg_type)
			self.tcp_send(data)
	
	def ping(self):
		if self.ws_status:
			data = "\x89\x80" + self.get_random_bytes(4)
			self.tcp_send(data)

	def pong(self):
		if self.ws_status:
			data = "\x8A\x80" + self.get_random_bytes(4)
			self.tcp_send(data)

	def close(self):
		if self.ws_status:
			data = "\x88\x80" + self.get_random_bytes(4)
			self.tcp_send(data)
	
	def open(self):
		self.log("Trying to connect ...")
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.connect((self.server, self.port))
			self.tcp_status = True
			self.start()
			sleep(3)
			self.connect()
		except:
			self.log("Error while establishing tcp connection ...")
			self.onerror(ERROR_TCP_CONNECTION)

	def connect(self):
		self.log("Initializing websocket handshake ...")
		self.key = base64.b64encode(self.get_random_bytes(16))
		message = 'GET / HTTP/1.1\r\n'
		message += 'Host: '+ self.server +'\r\n'
		message += 'Origin: http://www.websocket.org\r\n'
		message += 'Connection: Upgrade\r\n'
		message += 'Upgrade: websocket\r\n'
		if self.protocols:
			protocol_string = ", ".join(self.protocols)
			message += 'Sec-WebSocket-Protocol: '+ protocol_string +'\r\n'
		message += 'Sec-WebSocket-Key: '+ self.key +'\r\n'
		message += 'Sec-WebSocket-Version: 13\r\n\r\n'
		self.tcp_send(message)
	
	def disconnect(self):
		if self.tcp_status:
			try:
				self.socket.shutdown(socket.SHUT_RDWR)
				self.socket.close()
			except:
				self.onerror(ERROR_TCP_DISCONNECTION)

	def onresponse(self, data):
		self.log("On response called.")
		try:
			if self.ws_status:
				self.ws_framedata += data
				opcode = ord(self.ws_framedata[0]) & 15
				#print "Opcode: " + str(opcode)
					
				if (ord(self.ws_framedata[1]) > 128) or (opcode == 8):
					self.close()
					return
				
				frame_length = self.get_frame_length(self.ws_framedata)	
				if len(self.ws_framedata) >=  frame_length:
					frame = self.ws_framedata[:frame_length]
					self.ws_framedata = self.ws_framedata[frame_length:]
					
					if opcode == 1:
						self.onmessage(self.parse_data(frame), "text")
					elif opcode == 2:
						self.onmessage(self.parse_data(frame), "binary")
					elif opcode == 9:
						self.pong()
					elif opcode == 10:
						self.onmessage("Pong packet received ...", "text")
			else:
				response_dictionary = dict()
				response_header = data.split("\r\n\r\n")[0].split("\r\n")
				status_code = int(response_header[0].split()[1])
				
				if status_code != 101:
					self.log("Handshake request error ...")
					self.onerror(ERROR_WEBSOCKET_HANDSHAKE)
					return
				
				for header in response_header[1:]:
					parameter = header.split(":")[0].strip().lower()
					value = "".join(header.split(":")[1:]).strip()
					response_dictionary[parameter] = value
				
				status = False
				if "upgrade" in response_dictionary:
					if response_dictionary["upgrade"].lower() == "websocket":
						status = True
				
				if not status:
					self.log("No/Improper upgrade field in response ...")
					self.disconnect()
					self.onerror(ERROR_WEBSOCKET_HANDSHAKE_RESPONSE)
					return
				
				status = False
				if "connection" in response_dictionary:
					if response_dictionary["connection"].lower() == "upgrade":
						status = True
				
				if not status:
					self.log("No/Improper connection field in response ...")
					self.disconnect()
					self.onerror(ERROR_WEBSOCKET_HANDSHAKE_RESPONSE)
					return
				
				status = False
				if "sec-websocket-accept" in response_dictionary:
					sha_key = base64.b64encode(sha.new(self.key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
					if response_dictionary["sec-websocket-accept"] == sha_key:
						status = True
				
				if not status:
					self.log("No/Improper sec-websocket-accept field in response ...")
					self.disconnect()
					self.onerror(ERROR_WEBSOCKET_HANDSHAKE_RESPONSE)
					return
				
				status = True
				if self.protocols:
					if "sec-websocket-protocol" not in response_dictionary:
						status = False
				
				if not status:
					self.log("No/Improper protocol used for connect ...")
					self.disconnect()
					self.onerror(ERROR_WEBSOCKET_HANDSHAKE_RESPONSE)
					return
				
				self.log("Websocket handshake successful ...")
				self.ws_status = True
				self.onopen()
		except:
			self.log("Error decoding response ...")
			self.onerror(ERROR_DECODING_RESPONSE)
	
	def parse_data(self, data):
		payload_length_byte_1 = ord(data[1]) & 127
		
		if payload_length_byte_1 < 126:
			payload_length = payload_length_byte_1
			message = data[2:]
		elif payload_length_byte_1 == 126:
			payload_length = int((data[2:4]).encode("hex"),16)
			message = data[4:]
		elif payload_length_byte_1 == 127:
			payload_length = int((data[2:10]).encode("hex"),16)
			message = data[10:]
		else:
			message = ""
			self.log("Response too long ...")
			self.onerror(ERROR_WEBSOCKET_RESPONSE_TOO_LONG)
			return message

		#print "Payload Length: " + str(payload_length)
		return message
	
	def get_frame_length(self, data):
		payload_length_byte_1 = ord(data[1]) & 127
		
		if payload_length_byte_1 < 126:
			payload_length = payload_length_byte_1
			frame_length = payload_length + 2
		elif payload_length_byte_1 == 126:
			payload_length = int((data[2:4]).encode("hex"),16)
			frame_length = payload_length + 4
		elif payload_length_byte_1 == 127:
			payload_length = int((data[2:10]).encode("hex"),16)
			frame_length = payload_length + 10
		else:
			return -1
		return frame_length
	
	def tcp_send(self, data):
		try:
			self.socket.sendall(data)
		except:
			self.log("Cannot send tcp data ...")
			self.onerror(ERROR_TCP_SEND)

	def convert_data(self, message, msg_type):
		''' Initial byte indicating that this is the only websocket frame for the message and having text data '''
		if msg_type == "text":
			data = "\x81"
		else:
			data = "\x82"
		
		''' Select Masking Key '''
		masking_key = self.get_random_bytes(4)
		
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
			data = "\x88\x80" + masking_key	# Close connection if length exceeds pow(2,64)-1
			return data
		
		''' Merge Payload Length section and Masking Key '''
		binary_payload_length = self.xor_hex_strings("\x80", payload_length_byte_1) + payload_length_other_bytes + masking_key
		
		data += binary_payload_length
		data += self.xor_hex_strings(message,masking_key)
		return data
	
	def xor_hex_strings(self, xstr, ystr):
		xorstr = ""
		i = 0
		for x in xstr:
			y = ystr[i%len(ystr)]
			xorstr += chr(ord(x) ^ ord(y))
			i += 1
		return xorstr
	
	def get_random_bytes(self, count):
		random_bytes_string = ""
		for i in range(0,count):
			random_bytes_string += chr(random.randint(0, 255))
		
		return random_bytes_string
