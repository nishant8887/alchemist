package com.gigatech.websocket.dummyclient;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Client {

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		BufferedReader stdIn = new BufferedReader(new InputStreamReader(System.in));
		String userInput;
		
		WSClient client = new WSClient();
		client.setServer("websocket-nishantns.rhcloud.com","/",8000,null);
		client.open();
		
		while ((userInput = stdIn.readLine()) != null) {
			if(userInput.equals("ping"))
			{
				client.ping();
			}
			else if(userInput.equals("close"))
			{
				client.close();
			}
			else if(userInput.equals("open"))
			{
				client.open();
			}
			else if(userInput.equals("end"))
			{
				break;
			}
			else
			{
				client.send(userInput);
			}
		}
		stdIn.close();
	}

}
