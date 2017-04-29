/*
 * Utils.cpp
 *
 *  Created on: 02-Aug-2013
 *      Author: nishant8887
 */

#include "Utils.h"
#include <iostream>
#include <random>
#include <stdlib.h>

Utils::Utils() {

}

Utils::~Utils() {

}

std::string Utils::base64Encode(std::string charStr) {
	std::ostringstream base64estr;
	char table[65] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
	int size = charStr.length();

	std::string appendStr;

	switch(size % 3)
	{
		case 2:
			size++;
			charStr += char(0);
			appendStr = "=";
			break;
		case 1:
			size+=2;
			charStr += char(0);
			charStr += char(0);
			appendStr = "==";
			break;
		default:
			break;
	}

	for(int i=0; i <= size-3; i+=3) {
		base64estr << table[int((unsigned char)charStr[i] >> 2)];
		base64estr << table[int((((unsigned char)charStr[i] % 4) << 4) + ((unsigned char)charStr[i+1] >> 4))];
		base64estr << table[int((((unsigned char)charStr[i+1] % 16) << 2) + ((unsigned char)charStr[i+2] >> 6))];
		base64estr << table[int((unsigned char)charStr[i+2] % 64)];
	}

	return base64estr.str().replace((size/3 * 4)-appendStr.length(), appendStr.length(), appendStr);
}

std::string Utils::getRandomBytes(int size) {
	std::ostringstream randomStr;
	std::default_random_engine generator;
	std::uniform_int_distribution<int> distribution(0,255);
	int randomChar;

	for(int i=0; i < size; i++) {
		randomChar = distribution(generator);
		randomStr << char(randomChar);
	}
	return randomStr.str();
}

std::string Utils::convertToBytes(int number, int size) {
	std::string byteStr;
	for(int i=0; i < size; i++) {
		byteStr = char(number % 256) + byteStr;
		number = number >> 8;
	}
	return byteStr;
}

std::string Utils::xorStrings(std::string message, std::string maskingKey) {
	std::ostringstream resultStr;
	for(unsigned int i=0; i < message.length(); i++) {
		resultStr << (unsigned char)(char(maskingKey[i % maskingKey.length()]) ^ char(message[i]));
	}
	return resultStr.str();
}

std::string Utils::convertToHex(std::string message) {
	std::ostringstream resultStr;
	for(unsigned int i=0; i < message.length(); i++) {
		resultStr << std::hex << int((unsigned char)(message[i])) << " ";
	}
	return resultStr.str();
}
