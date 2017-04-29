package com.gigatech.websocket;

public class FrameLength {
	public int headerLength;
	public int payloadLength;
	
	public FrameLength(int hLength, int pLength)
	{
	    headerLength = hLength;
	    payloadLength = pLength;
	}
}
