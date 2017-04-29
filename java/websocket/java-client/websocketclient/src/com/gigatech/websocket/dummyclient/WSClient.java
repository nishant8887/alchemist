package com.gigatech.websocket.dummyclient;

import com.gigatech.websocket.WebsocketClient;
import com.gigatech.websocket.WebsocketErrors;

public class WSClient extends WebsocketClient {

	public WSClient() {
		super();
	}

	@Override
	public void onTextMessage(String message) {
		// TODO Auto-generated method stub
		System.out.println(message);
	}

	@Override
	public void onBinaryMessage(byte[] message) {
		// TODO Auto-generated method stub
		StringBuilder sb = new StringBuilder();
	    for (byte b : message) {
	        sb.append(String.format("%02X ", b));
	    }
	    System.out.println(sb.toString());
	}

	@Override
	public void onClose() {
		// TODO Auto-generated method stub
		System.out.println("WSCLIENT: Connection closed.");
	}

	@Override
	public void onOpen() {
		// TODO Auto-generated method stub
		System.out.println("WSCLIENT: Connection opened.");
	}

	@Override
	public void onError(WebsocketErrors type) {
		// TODO Auto-generated method stub
		System.out.println("WSCLIENT: Error occured - "+type.toString());
	}
}
