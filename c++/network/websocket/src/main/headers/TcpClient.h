/*
 * TcpClient.h
 *
 *  Created on: 31-Jul-2013
 *      Author: nishant8887
 */

#ifndef TCPCLIENT_H_
#define TCPCLIENT_H_

#include <netdb.h>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

#define BUFFER_SIZE 1024

enum TCP_ERROR_TYPE {
	ERROR_TCP_CONNECT,
	ERROR_TCP_SEND,
	ERROR_TCP_RECEIVE,
	ERROR_TCP_SHUTDOWN
};

class TcpClient {
private:
	int socketFd;
	sockaddr_in serverAddress;
	char *buffer;
	std::thread *receiver;
public:
	TcpClient();
	virtual ~TcpClient();
	virtual void setServer(std::string hostname, int port);
	void connect();
	void disconnect();
	virtual void send(std::string message);
	void receive();
	virtual void onmessage(std::string message);
	virtual void onopen();
	virtual void onclose();
	virtual void onerror(int errorType);
};

#endif /* TCPCLIENT_H_ */
