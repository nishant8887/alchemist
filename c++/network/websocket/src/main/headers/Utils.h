/*
 * Utils.h
 *
 *  Created on: 02-Aug-2013
 *      Author: nishant8887
 */

#ifndef UTILS_H_
#define UTILS_H_
#include <string>
#include <sstream>

class Utils {
private:
	Utils();
public:
	static std::string base64Encode(std::string charStr);
	static std::string getRandomBytes(int size);
	static std::string convertToBytes(int number, int size);
	static std::string xorStrings(std::string message, std::string maskingKey);
	static std::string convertToHex(std::string message);
	virtual ~Utils();
};

#endif /* UTILS_H_ */
