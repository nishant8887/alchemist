/*
 * IWebsocket.cpp
 *
 *  Created on: Aug 3, 2013
 *      Author: nishant8887
 */

#include "WebsocketClient.h"
#include "IWebsocket.h"

IWebsocket::IWebsocket() {
	wClient = NULL;
}

IWebsocket::IWebsocket(std::string serverName, int serverPort, std::string serverAppRoot) {
	wClient = new WebsocketClient(this);
	wClient->setServer(serverName, serverPort, serverAppRoot);
}

IWebsocket::~IWebsocket() {

}

void IWebsocket::open() {
	wClient->open();
}

void IWebsocket::close() {
	wClient->close();
}

void IWebsocket::send(std::string message) {
	wClient->send(message, TEXT);
}

void IWebsocket::onopen() {
	std::cout << "Connection opened ..." << std::endl;
}

void IWebsocket::onclose() {
	std::cout << "Connection closed ..." << std::endl;
}

void IWebsocket::onmessage(std::string message, int messageType) {
	std::cout << "Message received ..." << std::endl;
	if(messageType == TEXT) {
		std::cout << message << std::endl;
	}
}

void IWebsocket::onerror(int errorType) {
	std::cout << "Error occured ..." << std::endl;
}
