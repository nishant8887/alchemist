/*
 * IWebsocket.h
 *
 *  Created on: Aug 3, 2013
 *      Author: nishant8887
 */

#ifndef IWEBSOCKET_H_
#define IWEBSOCKET_H_

class WebsocketClient;

class IWebsocket {
private:
	WebsocketClient *wClient;
	IWebsocket();
public:
	IWebsocket(std::string serverName, int serverPort, std::string serverAppRoot);
	virtual ~IWebsocket();
	void open();
	void close();
	void send(std::string message);
	virtual void onopen();
	virtual void onclose();
	virtual void onmessage(std::string message, int messageType);
	virtual void onerror(int errorType);
};

#endif /* IWEBSOCKET_H_ */
