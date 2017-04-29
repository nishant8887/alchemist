/*
 * Logger.h
 *
 *  Created on: 06-Aug-2013
 *      Author: nishant8887
 */

#ifndef LOGGER_H_
#define LOGGER_H_
#include <string>

enum LOG_LEVEL_TYPE {
	OFF = 0,
	ERROR,
	WARN,
	INFO,
	DEBUG
};

class Logger {
private:
	static unsigned int logLevel;
public:
	static void setLevel(unsigned int level);
	static unsigned int getLevel();
	static void info(std::string message);
	static void error(std::string message);
	static void warn(std::string message);
	static void debug(std::string message);
};

#endif /* LOGGER_H_ */
