package com.gigatech.websocket;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.logging.Logger;

import org.apache.commons.codec.binary.Base64;

public abstract class WebsocketClient implements Runnable
{
	private static final int RECEIVE_BUFFER_SIZE = 1024;
	private Socket socket = null;
	private InputStream in = null;
	private OutputStream out = null;
	private String server = null;
	private int port;
	private String protocols = null;
	private String url;
	private String key;
	private Boolean websocketEnabled = Boolean.FALSE;
	private ByteArrayOutputStream inputStream;
	private Logger clientLogger;
	
	public WebsocketClient()
	{
		clientLogger = Logger.getLogger("WebsocketClient");
	}
	
	public void setServer(String serverAddress, String serverURL, int serverPort, String serverProtocols)
	{
		server = serverAddress;
		port = serverPort;
		url = serverURL;
		protocols = serverProtocols;
	}
	
	public abstract void onTextMessage(String message);
	
	public abstract void onBinaryMessage(byte[] message);
	
	public abstract void onClose();
	
	public abstract void onOpen();
	
	public abstract void onError(WebsocketErrors type);
	
	public void open()
	{
	    try
	    {
			socket = new Socket(server, port);
			in = socket.getInputStream();
			out = socket.getOutputStream();
			inputStream = new ByteArrayOutputStream();
			new Thread(this).start();
			connect();
	    } catch(Exception e) {
	    	clientLogger.info("Error connecting to host or host doesn't exist.");
	    	onError(WebsocketErrors.TCP_CONNECT_ERROR);
	    }
	}
	
	public void send(String message)
	{
	    if(!websocketEnabled) return;
	    if(message == null) return;
	    byte[] data = convertData(message);
	    if (data != null)
	    {
	    	tcpSend(data);
	    }
	}
	
	public void send(byte[] message)
	{
	    if(!websocketEnabled) return;
	    if(message == null) return;
	    byte[] data = convertData(message);
	    if (data != null)
	    {
	    	tcpSend(data);
	    }
	}
	
	public void ping()
	{
	    // 89 80
		byte[] startbytes = { (byte)137, (byte)128 };
		sendSpecialPacket(startbytes);
	}

	public void pong()
	{
	    // 8A 80
	    byte[] startbytes = { (byte)138, (byte)128 };
	    sendSpecialPacket(startbytes);
	}
	
	public void close()
	{
	    // 88 80
	    byte[] startbytes = { (byte)136, (byte)128 };
	    sendSpecialPacket(startbytes);
	}
	
	public void run()
	{
	    int insize = 0;
	    byte[] response = new byte[RECEIVE_BUFFER_SIZE];
	    try
	    {
			while((insize = in.read(response)) != -1) {
			    processResponse(response, insize);
			    response = new byte[RECEIVE_BUFFER_SIZE];
			}
	    } catch(Exception e) {
	    }
	    clientLogger.info("Connection closed at TCP level.");
	    disconnect();
	    clientLogger.info("Websocket client shutdown.");
	}
	
	private void sendSpecialPacket(byte[] startbytes)
	{
		if(!websocketEnabled) return;
	    try
	    {
			ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
			outputStream.write(startbytes);
			outputStream.write(getRandomBytes(4));
			byte data[] = outputStream.toByteArray();
			tcpSend(data);
	    } catch(Exception e) {
	    	clientLogger.info("Error in packing bytes.");
	    }
	}
	
	private void connect()
	{
	    String message;
	    clientLogger.info("Initializing websocket handshake.");	    
	    key = new String(Base64.encodeBase64(getRandomBytes(16)));
	    message = "GET "+ url +" HTTP/1.1\r\n";
	    message += "Host: "+ server +"\r\n";
	    message += "Origin: http://www.websocket.org\r\n";
	    message += "Connection: Upgrade\r\n";
	    message += "Upgrade: websocket\r\n";
	    if(protocols != null)
	    {
	    	message += "Sec-WebSocket-Protocol: "+ protocols +"\r\n";
	    }
	    message += "Sec-WebSocket-Key: "+ key +"\r\n";
	    message += "Sec-WebSocket-Version: 13\r\n\r\n";
	    tcpSend(message);
	}
	
	private void disconnect()
	{
	    try
	    {
			in.close();
			out.close();
			socket.close();
			clientLogger.info("Connection closed.");
			websocketEnabled = Boolean.FALSE;
			onClose();
	    } catch(Exception e) {
	    	clientLogger.info("Error closing socket.");
	    	onError(WebsocketErrors.TCP_DISCONNECT_ERROR);
	    }
	}
	
	private void tcpSend(String data)
	{
	    byte[] bytedata = getBytes(data);
	    try
	    {
	    	out.write(bytedata, 0, bytedata.length);
	    } catch(Exception e) {
	    	clientLogger.info("Error sending data to the server.");
	    	onError(WebsocketErrors.TCP_SEND_ERROR);
	    }
	}
	
	private void tcpSend(byte[] data)
	{
	    try
	    {
	    	out.write(data, 0, data.length);
	    } catch(Exception e) {
	    	clientLogger.info("Error sending data to the server.");
	    	onError(WebsocketErrors.TCP_SEND_ERROR);
	    }
	}
	
	private byte[] convertData(String message)
	{
	    try
	    {
			ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
			
			byte[] startbytes = { (byte)129 };
			byte[] payloadHeader = {};
			byte[] maskingKey = getRandomBytes(4);
			byte[] messageBytes = getBytes(message, maskingKey);
			int payloadLength = messageBytes.length;
			
			if (payloadLength < 126)
			{
			    payloadHeader = new byte[1];
			    payloadHeader[0] = (byte)(128 ^ payloadLength);
			} else if (payloadLength < Math.pow(2,16))
			{
			    payloadHeader = new byte[3];
			    payloadHeader[0] = (byte)(128 ^ 126);
			    for(int i = 1; i <= 2; i++)
			    {
			    	payloadHeader[i] = (byte)(payloadLength >> (8*(2-i)));
			    }
			} else if (payloadLength < Math.pow(2,64))
			{
			    payloadHeader = new byte[9];
			    payloadHeader[0] = (byte)(128 ^ 127);
			    for(int i = 1; i <= 8; i++)
			    {
			    	payloadHeader[i] = (byte)(payloadLength >> (8*(8-i)));
			    }
			} else {
			    return null;
			}
			outputStream.write(startbytes);
			outputStream.write(payloadHeader);
			outputStream.write(maskingKey);
			outputStream.write(messageBytes);
			return outputStream.toByteArray();
	    } catch(Exception e) {
			clientLogger.info("Error in packing bytes.");
			onError(WebsocketErrors.WEBSOCKET_SEND_ERROR);
			return null;
	    }
	}
	
	private byte[] convertData(byte[] message)
	{
	    try
	    {
			ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
			
			byte[] startbytes = { (byte)130 };
			byte[] payloadHeader = {};
			byte[] maskingKey = getRandomBytes(4);
			byte[] messageBytes = xorByteArrays(message, maskingKey);
			int payloadLength = messageBytes.length;
			
			if (payloadLength < 126)
			{
			    payloadHeader = new byte[1];
			    payloadHeader[0] = (byte)(128 ^ payloadLength);
			} else if (payloadLength < Math.pow(2,16))
			{
			    payloadHeader = new byte[3];
			    payloadHeader[0] = (byte)(128 ^ 126);
			    for(int i = 1; i <= 2; i++)
			    {
			    	payloadHeader[i] = (byte)(payloadLength >> (8*(2-i)));
			    }
			} else if (payloadLength < Integer.MAX_VALUE) // Integer.MAX_VALUE used instead of Math.pow(2,64)
			{
			    payloadHeader = new byte[9];
			    payloadHeader[0] = (byte)(128 ^ 127);
			    for(int i = 1; i <= 8; i++)
			    {
			    	payloadHeader[i] = (byte)(payloadLength >> (8*(8-i)));
			    }
			} else {
			    return null;
			}
			outputStream.write(startbytes);
			outputStream.write(payloadHeader);
			outputStream.write(maskingKey);
			outputStream.write(messageBytes);
			return outputStream.toByteArray();
	    } catch(Exception e) {
			clientLogger.info("Error in packing bytes.");
			onError(WebsocketErrors.WEBSOCKET_SEND_ERROR);
			return null;
	    }
	}
	
	private void processResponse(byte[] rbytes, int size)
	{
	    try
	    {
			inputStream.write(rbytes, 0, size);
			if(websocketEnabled)
			{
			    // Check Websocket Frame
			    byte[] streambytes = inputStream.toByteArray();
			    FrameLength frameLength = getLength(streambytes);
			    int expectedFrameLength = frameLength.headerLength + frameLength.payloadLength;
			    if(expectedFrameLength == -1)
			    {
			    	inputStream = new ByteArrayOutputStream();
			    	onError(WebsocketErrors.WEBSOCKET_RECEIVE_ERROR);
			    }
			    else if(streambytes.length >= expectedFrameLength)
			    {
					inputStream = new ByteArrayOutputStream();
					inputStream.write(streambytes, expectedFrameLength, streambytes.length - expectedFrameLength);
					byte[] frame = Arrays.copyOfRange(streambytes, 0, expectedFrameLength);
					processFrame(frame, frameLength.headerLength);
			    }
			}
			else
			{
			    // Check HTTP Response headers
			    String header = inputStream.toString();
			    System.out.print(header);
			    if(header.substring(header.length() - 4, header.length()).equals("\r\n\r\n"))
			    {
			    	inputStream = new ByteArrayOutputStream();
				    websocketEnabled = processHeader(header);
				    if(!websocketEnabled) {
				    	onError(WebsocketErrors.WEBSOCKET_HANDSHAKE_RESPONSE_FIELD_ERROR);
				    	disconnect();
				    } else {
				    	clientLogger.info("Connection opened.");
				    	onOpen();
				    }
			    }
			}
	    } catch(Exception e) {
	    }
	}
	
	private void processFrame(byte[] frame, int headerLength)
	{
	    int opcode = (frame[0] & 15);
	    byte[] data;
	    switch(opcode)
	    {
			case 1:
			    data = Arrays.copyOfRange(frame, headerLength, frame.length);
			    String dataStr = new String(data);
			    onTextMessage(dataStr);
			    break;
			case 2:
			    data = Arrays.copyOfRange(frame, headerLength, frame.length);
			    onBinaryMessage(data);
			    break;
			case 9:
			    pong();
			    break;
			case 10:
			    clientLogger.info("Pong packet received.");
			    break;
			default:
	    }
	}
	
	private Boolean processHeader(String header)
	{
	    // Check for HTTP response headers
		int fieldsChecked = 0;
		Boolean status = true;
		String[] fields = header.split("\r\n");
		String[] statusField = fields[0].split(" ");
		
		try
		{
			if(!statusField[0].trim().toLowerCase().equals("http/1.1")) status = false;
			if(!statusField[1].trim().toLowerCase().equals("101")) status = false;
		} catch(Exception e) {
			status = false;
		}
		
		for(String f: fields)
		{
			if(!status)
			{
				return Boolean.FALSE;
			}
			try
			{
				String[] fparts = f.split(":");
				String parameter = fparts[0].trim();
				String value = fparts[1].trim();
				
				if(parameter.equalsIgnoreCase("upgrade"))
				{
					fieldsChecked++;
					if(!value.equalsIgnoreCase("websocket")) status = false;
				} else if(parameter.equalsIgnoreCase("connection"))
				{
					fieldsChecked++;
					if(!value.equalsIgnoreCase("upgrade")) status = false;
				} else if(parameter.equalsIgnoreCase("sec-websocket-accept"))
				{
					fieldsChecked++;
					MessageDigest shaKey = MessageDigest.getInstance("SHA");
					shaKey.update(getBytes(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"));
					String shaKeyDigest = new String(Base64.encodeBase64(shaKey.digest()));
					if(!value.equals(shaKeyDigest)) {
						status = false;
					}
				}
				// Protocol field check not done.
			} catch(Exception e) {
				
			}
		}
		if(fieldsChecked < 3) return Boolean.FALSE;
		return Boolean.TRUE;
	}
	
	private FrameLength getLength(byte[] framepart)
	{
	    int headerLength = 0;
	    int payloadLength = (int)(framepart[1] & (byte)127);
	    
	    if(payloadLength < 126)
	    {
	    	headerLength = 2;
	    }
	    else if(payloadLength == 126)
	    {
			payloadLength = ((framepart[2] & 0xFF) << 8) + (framepart[3] & 0xFF);
			headerLength = 4;
	    }
	    else if(payloadLength == 127)
	    {
			if (((int)(framepart[2]) > 0) || ((int)(framepart[3]) > 0) || ((int)(framepart[4]) > 0) || ((int)(framepart[5]) > 0))
			{
			    payloadLength = -1;
			}
			else
			{
			    payloadLength = 0;
			    for (int i = 0; i < 4; i++) {
				payloadLength += (framepart[6+i] & 0xFF) << ((4-1-i)*8);
			    }
			    headerLength = 10;
			}
	    }
	    else
	    {
	    	payloadLength = -1;
	    }
	    return (new FrameLength(headerLength, payloadLength));
	}
	
	private byte[] getRandomBytes(int size)
	{
	    byte[] byteArray = new byte[size];
	    for(int i=0; i < size; i++)
	    {
	    	byteArray[i] = ((byte)(Math.random() * 256));
	    }
	    return byteArray;
	}
	
	private byte[] getBytes(String bytestring)
	{
	    byte[] byteArray = new byte[bytestring.length()];
	    for(int i = 0; i < bytestring.length(); i++)
	    {
	    	byteArray[i] = (byte) bytestring.charAt(i);
	    }
	    return byteArray;
	}
	
	private byte[] getBytes(String bytestring, byte[] maskingKey)
	{
	    byte[] byteArray = new byte[bytestring.length()];
	    for(int i = 0; i < bytestring.length(); i++)
	    {
	    	byteArray[i] = (byte) (bytestring.charAt(i) ^ maskingKey[i % maskingKey.length]);
	    }
	    return byteArray;
	}
	
	private byte[] xorByteArrays(byte[] message, byte[] maskingKey)
	{
	    byte[] result = new byte[message.length];
	    for(int i = 0; i < message.length; i++)
	    {
	    	result[i] = (byte) (message[i] ^ maskingKey[i % maskingKey.length]);
	    }
	    return result;
	}
}
