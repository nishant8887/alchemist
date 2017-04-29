/*
 * Logger.cpp
 *
 *  Created on: 06-Aug-2013
 *      Author: nishant8887
 */

#include "Logger.h"
#include <iostream>

unsigned int Logger::logLevel = DEBUG;

void Logger::setLevel(unsigned int level) {
	if(Logger::logLevel <= DEBUG) {
		Logger::logLevel = level;
	}
}

unsigned int Logger::getLevel() {
	return Logger::logLevel;
}

void Logger::info(std::string message) {
	if(Logger::logLevel >= INFO) {
		std::cout << "[INFO] " << message << std::endl;
	}
}

void Logger::error(std::string message) {
	if(Logger::logLevel >= ERROR) {
		std::cout << "[ERROR] " << message << std::endl;
	}
}

void Logger::warn(std::string message) {
	if(Logger::logLevel >= WARN) {
		std::cout << "[WARN] " << message << std::endl;
	}
}

void Logger::debug(std::string message) {
	if(Logger::logLevel >= DEBUG) {
		std::cout << "[DEBUG] " << message << std::endl;
	}
}
