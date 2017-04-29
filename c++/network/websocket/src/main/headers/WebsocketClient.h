/*
 * WebsocketClient.h
 *
 *  Created on: 31-Jul-2013
 *      Author: nishant8887
 */

#ifndef WEBSOCKETCLIENT_H_
#define WEBSOCKETCLIENT_H_

#include "TcpClient.h"
#include "IWebsocket.h"
#define DEFAULT_ORIGIN "http://www.websocket.org"

enum MESSAGE_TYPE {
	TEXT = 1,
	BINARY = 2,
};

enum WS_ERROR_TYPE {
	ERROR_WEBSOCKET_HANDSHAKE = 4,
	ERROR_WEBSOCKET_RECEIVE,
};

struct FrameLength {
	int headerLength;
	unsigned int frameLength;
};

class WebsocketClient : private TcpClient {
private:
	std::string serverName;
	std::string hostName;
	std::string applicationRoot;
	std::string key;
	std::string protocols;
	bool websocketEnabled;
	std::ostringstream inputStream;
	std::string convertData(std::string message, int messageType);
	void processFrame(std::string frame, int headerLength);
	FrameLength getLengthOfFrame(std::string frame);
	void sendSpecialFrame(int opcode);
	void pong();
	void onmessage(std::string message);
	void onopen();
	void onclose();
	void onerror(int errorType);
	IWebsocket *interface;
	WebsocketClient();
public:
	WebsocketClient(IWebsocket *callbackClass);
	virtual ~WebsocketClient();
	void setServer(std::string hostname, int port, std::string appRoot, std::string protocolsList = "", std::string origin = DEFAULT_ORIGIN);
	void send(std::string message, int messageType);
	void open();
	void ping();
	void close();
};

#endif /* WEBSOCKETCLIENT_H_ */
