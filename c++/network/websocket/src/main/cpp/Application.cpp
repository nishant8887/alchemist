/*
 * Application.cpp
 *
 *  Created on: 31-Jul-2013
 *      Author: nishant8887
 */
#include "Application.h"

int main()
{
	IWebsocket wClient("localhost", 50007, "/");
	//std::string protocols = "dumb-increment-protocol, dummy-protocol, chindi-protocol";
	wClient.open();

	std::string command;
	while(1) {
		std::cin >> command;
		if (command == "end") {
			break;
		} else {
			wClient.send(command);
		}
	}
	wClient.close();
	return 0;
}
