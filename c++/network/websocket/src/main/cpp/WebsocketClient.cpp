/*
 * WebsocketClient.cpp
 *
 *  Created on: 31-Jul-2013
 *      Author: nishant8887
 */

#include "WebsocketClient.h"
#include "Logger.h"
#include "Utils.h"

WebsocketClient::WebsocketClient() {
	websocketEnabled = false;
	interface = NULL;
}

WebsocketClient::WebsocketClient(IWebsocket *callbackClass) {
	websocketEnabled = false;
	interface = callbackClass;
}

WebsocketClient::~WebsocketClient() {

}

void WebsocketClient::setServer(std::string hostname, int port, std::string appRoot, std::string protocolsList, std::string origin) {
	serverName = hostname;
	hostName = origin;
	applicationRoot = appRoot;
	protocols = protocolsList;
	TcpClient::setServer(hostname, port);
}

void WebsocketClient::onopen() {
	Logger::debug("Initializing websocket handshake.");
	this->key = Utils::base64Encode(Utils::getRandomBytes(16));
	std::string handshakeString = "GET " + this->applicationRoot + " HTTP/1.1\r\n";
	handshakeString += "Host: " + this->serverName + "\r\n";
	handshakeString += "Origin: " + this->hostName + "\r\n";
	handshakeString += "Connection: Upgrade\r\n";
	handshakeString += "Upgrade: websocket\r\n";
	handshakeString += "Sec-WebSocket-Key: " + this->key + "\r\n";
	if(!this->protocols.empty()) {
		handshakeString += "Sec-WebSocket-Protocol: " + this->protocols + "\r\n";
	}
	handshakeString += "Sec-WebSocket-Version: 13\r\n\r\n";
	TcpClient::send(handshakeString);
}

void WebsocketClient::onclose() {
	interface->onclose();
}

void WebsocketClient::onerror(int errorType) {
	interface->onerror(errorType);
}

void WebsocketClient::onmessage(std::string message) {
	inputStream << message;
	if(websocketEnabled) {
		// Check Websocket Frame
		std::string streambytes = inputStream.str();
		FrameLength frameLength = getLengthOfFrame(streambytes);
		unsigned int expectedFrameLength = frameLength.frameLength;
		if(frameLength.headerLength == -1)
		{
			inputStream.str("");
			inputStream.clear();
			interface->onerror(ERROR_WEBSOCKET_RECEIVE);
			this->close();
		}
		else if(streambytes.length() >= expectedFrameLength)
		{
			inputStream.str("");
			inputStream.clear();
			inputStream << streambytes.substr(expectedFrameLength);
			processFrame(streambytes.substr(0, expectedFrameLength), frameLength.headerLength);
		}
	} else {
		// Check HTTP Headers
		websocketEnabled = true;
		Logger::debug("Websocket handshake successful.");
		inputStream.str("");
		inputStream.clear();
	}
}

void WebsocketClient::processFrame(std::string frame, int headerLength) {
	int opcode = int((unsigned char)(frame[0] & 15));
	std::string data;
	switch(opcode)
	{
		case 1:
			data = frame.substr(headerLength);
			std::cout << data << std::endl;
			interface->onmessage(data, TEXT);
			break;
		case 2:
			data = frame.substr(headerLength);
			std::cout << data << std::endl;
			interface->onmessage(data, BINARY);
			break;
		case 9:
			Logger::info("Ping packet received. Sending pong.");
			pong();
			break;
		case 10:
			Logger::info("Pong packet received.");
			break;
		default:
			break;
	}
}

void WebsocketClient::send(std::string message, int messageType) {
	TcpClient::send(this->convertData(message,messageType));
}

void WebsocketClient::ping() {
	sendSpecialFrame(137);
}

void WebsocketClient::pong() {
	sendSpecialFrame(138);
}

void WebsocketClient::close() {
	sendSpecialFrame(136);
	TcpClient::disconnect();
}

void WebsocketClient::open() {
	TcpClient::connect();
}

void WebsocketClient::sendSpecialFrame(int opcode) {
	std::ostringstream Packet;
	std::string maskingKey = Utils::getRandomBytes(4);
	Packet << (unsigned char)(opcode) << (unsigned char)(128) << maskingKey;
	TcpClient::send(Packet.str());
}

std::string WebsocketClient::convertData(std::string message, int messageType) {
	std::ostringstream msgPacket;

	if(messageType == TEXT) {
		msgPacket << (unsigned char)(129);
	} else if(messageType == BINARY){
		msgPacket << (unsigned char)(130);
	}
	std::string maskingKey = Utils::getRandomBytes(4);
	unsigned int payloadLength = message.length();

	if(payloadLength < 126) {
		msgPacket << (unsigned char)(char(128) ^ char(payloadLength));
	} else if(payloadLength < 65536) {
		msgPacket << (unsigned char)(char(128) ^ char(126));
		msgPacket << Utils::convertToBytes(payloadLength, 2);
	} else if(payloadLength < 4294967295) {
		msgPacket << (unsigned char)(char(128) ^ char(127));
		msgPacket << Utils::convertToBytes(payloadLength, 8);
	} else {
		Logger::error("Too big message to be sent.");
		this->close();
	}
	msgPacket << maskingKey;
	msgPacket << Utils::xorStrings(message, maskingKey);
	return msgPacket.str();
}

FrameLength WebsocketClient::getLengthOfFrame(std::string frame) {
	int headerLength = 0;
	unsigned int frameLength = 0;
	unsigned int payloadLength = (unsigned int)((unsigned char) (frame[1] & char(127)));
	if(payloadLength < 126) {
		frameLength = payloadLength;
		headerLength = 2;
	} else if(payloadLength == 126) {
		frameLength = (unsigned int)((unsigned char)frame[2] << 8) + (unsigned int) ((unsigned char)frame[3]);
		headerLength = 4;
	} else if(payloadLength == 127) {
		if (((int)((unsigned char) frame[2]) > 0) || ((int)((unsigned char) frame[3]) > 0) || ((int)((unsigned char) frame[4]) > 0) || ((int)((unsigned char) frame[5]) > 0))
		{
			frameLength = 0;
			headerLength = -1;
			Logger::error("Too big message received.");
			return FrameLength({headerLength, frameLength});
		}
		for (int i=0; i < 4; i++) {
			frameLength += (unsigned int)((unsigned char)frame[6+i] << ((4-1-i)*8));
		}
		headerLength = 10;
	}
	frameLength += headerLength;
	return FrameLength({headerLength, frameLength});
}
