/*
 * TcpClient.cpp
 *
 *  Created on: 31-Jul-2013
 *      Author: nishant8887
 */

#include "TcpClient.h"
#include "Logger.h"
#include <cstring>
#include <sstream>
#include <unistd.h>

TcpClient::TcpClient() {
	socketFd = socket(AF_INET, SOCK_STREAM, 0);
	buffer = NULL;
	receiver = NULL;
}

TcpClient::~TcpClient() {
	close(socketFd);
}

void TcpClient::connect() {
	int success = ::connect(socketFd, (sockaddr *)&serverAddress, sizeof(serverAddress));
	if(success == -1) {
		Logger::error("TCP connect failed.");
		this->onerror(ERROR_TCP_CONNECT);
		return;
	}
	Logger::debug("TCP connection opened.");
	receiver = new std::thread([this]() { this->receive(); });
	receiver->detach();
	Logger::debug("TCP receiver thread started.");
	this->onopen();
}

void TcpClient::send(std::string message) {
	int success = ::send(socketFd, message.c_str(), message.length(), 0);
	if(success == -1) {
		Logger::error("TCP send failed.");
		this->onerror(ERROR_TCP_SEND);
		return;
	}
	Logger::debug("TCP message sent.");
}

void TcpClient::receive() {
	buffer = new char[BUFFER_SIZE];
	while(true) {
		int size = recv(socketFd, buffer, BUFFER_SIZE, 0);
		if(size <= 0) {
			if(size == -1) {
				Logger::error("TCP receive failed.");
				this->onerror(ERROR_TCP_RECEIVE);
			}
			break;
		}
		Logger::debug("TCP message received.");
		std::ostringstream message;
		message.write(buffer, size);
		this->onmessage(message.str());
	}
	Logger::debug("TCP receiver thread shutdown.");
	this->disconnect();
}

void TcpClient::disconnect() {
	int success = shutdown(socketFd, 2);
	if(success == -1) {
		Logger::error("TCP shutdown failed.");
		this->onerror(ERROR_TCP_SHUTDOWN);
		return;
	}
	Logger::debug("TCP connection shutdown.");
	this->onclose();
}

void TcpClient::setServer(std::string hostname, int port) {
	hostent *hostEntity = gethostbyname(hostname.c_str());
	memcpy(&serverAddress.sin_addr, hostEntity->h_addr_list[0], hostEntity->h_length);
	serverAddress.sin_family = AF_INET;
	serverAddress.sin_port = htons(port);
}

void TcpClient::onerror(int errorType) {

}

void TcpClient::onopen() {

}

void TcpClient::onclose() {

}

void TcpClient::onmessage(std::string message) {

}
