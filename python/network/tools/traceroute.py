import socket
from threading import Thread
from time import time, sleep

class Packet(object):
    def __init__(self, *args):
        self.version = 4
        self.ihl = 5
        self.dscp = 0
        self.ecn = 0
        self.identification = 1
        self.ttl = 64
        self.protocol = 255
        self.flagDF = 0
        self.flagMF = 0
        self.fragmentOffset = 0
        self.source = "127.0.0.1"
        self.destination = "127.0.0.1"
        self.optionBytes = ""
        self.data = ""
        self.message = ""
        
        totalargs = len(args)
        if totalargs == 1:
            self.data = args[0]
        elif totalargs == 3:
            self.source = args[0]
            self.destination = args[1]
            self.message = args[2]

    def makePacket(self):
        self.data = ""
        self.ihl = 5 + int(len(self.optionBytes)/4)
        
        self.data += chr((self.version << 4) + self.ihl)
        self.data += chr((self.dscp << 2) + self.ecn)
        
        totalLength = self.ihl * 4 + len(self.message)
        self.data += chr((totalLength >> 8) % 256)
        self.data += chr(totalLength % 256)
        
        self.data += chr((self.identification >> 8) % 256)
        self.data += chr(self.identification % 256)
        
        self.data += chr((self.fragmentOffset >> 8) % 32 + (self.flagDF << 6) + (self.flagMF << 5))
        self.data += chr(self.fragmentOffset % 256)
        
        self.data += chr(self.ttl)
        self.data += chr(self.protocol)
        
        part = ""
        part += self.getAddressBytes(self.source)
        part += self.getAddressBytes(self.destination)
        part += self.optionBytes
        
        checksum = self.getCheckSum(self.data + part)
        self.data += checksum
        self.data += part
        
        self.data += self.message
    
    def parsePacket(self):
        self.version = ord(self.data[0]) >> 4
        self.ihl = ord(self.data[0]) % 16
        self.dscp = ord(self.data[1]) >> 2
        self.ecn = ord(self.data[1]) % 4
        self.identification = ord(self.data[4]) * 256 + ord(self.data[5])
        self.ttl = ord(self.data[8])
        self.protocol = ord(self.data[9])
        self.flagDF = (ord(self.data[6]) >> 6) % 2
        self.flagMF = (ord(self.data[6]) >> 5) % 2
        self.fragmentOffset = (ord(self.data[6]) % 32) * 256 + ord(self.data[7])
        self.source = self.getAddress("source")
        self.destination = self.getAddress("destination")
        self.optionBytes = self.data[20:self.ihl*4]
        self.message = self.data[self.ihl*4:]
    
    def checkPacket(self):
        if not (self.ihl == 5 + int(len(self.optionBytes)/4)):
            return False
        
        totalLength = ord(self.data[2]) * 256 + ord(self.data[3])
        if not (totalLength == len(self.data)):
            return False
        
        if not (self.getCheckSum(self.data[:(self.ihl*4)]) == "\x00\x00"):
            return False
        return True
    
    def getAddressBytes(self, address):
        result = ""
        for addressByte in address.split("."):
            result += chr(int(addressByte))
        return result

    def getCheckSum(self, wordStr):
        wordsum = 0
        for i in range(0,len(wordStr),2):
            wordsum += ord(wordStr[i]) * 256 + ord(wordStr[i+1])
        
        checksumValue = wordsum % pow(2,16) + (wordsum >> 16)
        checksum = chr(~(checksumValue >> 8) % 256)
        checksum += chr(~checksumValue % 256)
        return checksum
    
    def getAddress(self, typeStr):
        if typeStr == "source":
            i = 12
        elif typeStr == "destination":
            i = 16
        try:
            addressStr = str(ord(self.data[i])) + "." + str(ord(self.data[i+1])) + "." + str(ord(self.data[i+2])) + "." + str(ord(self.data[i+3]))
        except:
            addressStr = None
        return addressStr

    def showPacketDetails(self, showmsg=True):
        print "IP Header"
        print "Version: " + str(self.version)
        print "Header Length: " + str(self.ihl)
        print "DSCP: " + str(self.dscp) + ", ECN: " + str(self.ecn)
        print "Identification: " + str(self.identification)
        print "Time To Live: " + str(self.ttl)
        print "Protocol: " + str(self.protocol)
        print "DF: " + str(self.flagDF) + ", MF: " + str(self.flagMF)
        print "Fragment Offset: " + str(self.fragmentOffset)
        print "Source: " + self.source
        print "Destination: " + self.destination
        print "Optional Header (HEX): " + self.optionBytes.encode("hex")
        if showmsg:
            print "IP Message (HEX)"
            print self.message.encode("hex")

class ICMPPacket(Packet):
    def __init__(self, *args):
        self.type = 8
        self.code = 0
        self.icmpExtraHeader = "\x00\x00\x00\x00"
        self.icmpMessage = ""
        
        totalargs = len(args)
        if totalargs <= 1:
            super(ICMPPacket, self).__init__(*args)
        elif totalargs == 2:
            self.source = args[0]
            self.destination = args[1]
            super(ICMPPacket, self).__init__(self.source, self.destination, "")
        
        self.protocol = 1
    
    def makePacket(self):
        self.message = chr(self.type) + chr(self.code)
        restData = (self.icmpExtraHeader + self.icmpMessage)
        checksum = self.getCheckSum(self.message + restData)
        self.message += checksum + restData
        super(ICMPPacket, self).makePacket()

    def parsePacket(self):
        super(ICMPPacket, self).parsePacket()
        self.type = ord(self.message[0])
        self.code = ord(self.message[1])
        self.icmpExtraHeader = self.message[4:8]
        self.icmpMessage = self.message[8:]
    
    def checkPacket(self):
        if not (self.getCheckSum(self.message) == "\x00\x00"):
            return False
        return super(ICMPPacket, self).checkPacket()

    def showPacketDetails(self):
        super(ICMPPacket, self).showPacketDetails(False)
        print "ICMP Header"
        print "Type: " + str(self.type)
        print "Code: " + str(self.code)
        print "Extra Header (HEX): " + self.icmpExtraHeader.encode("hex")
        print "ICMP Message (HEX)"
        print self.icmpMessage.encode("hex")

class Receiver(Thread):
    
    def __init__(self):
        self.listen = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.packet = ICMPPacket()
        self.destination = "173.194.113.191"
        self.node = ""
        super(Receiver, self).__init__()
    
    def run(self):
        while self.listen:
            try:
                data = self.socket.recv(1024,0)
                self.packet.data = data
                self.packet.parsePacket()
                if self.packet.type == 0 and self.packet.code == 0:
                    if self.packet.icmpMessage[0:8] == "\x4e\x69\x73\x68\x61\x6e\x74\x2e":
                        traveltime = int(time() * 1000) - self.parseTimeStamp(self.packet.icmpMessage[8:])
                        print str(traveltime) + " milliseconds"
                if self.packet.type == 11 and self.packet.code == 0:
                    newpacket = ICMPPacket(self.packet.icmpMessage)
                    newpacket.parsePacket()
                    if newpacket.destination == self.destination:
                        if self.node != self.packet.source:
                            self.node = self.packet.source
                            print self.packet.source
            except:
                break
    
    def parseTimeStamp(self, timeStr):
        time = 0
        while timeStr != "":
            time = time * pow(2,16) + ord(timeStr[0]) * 256 + ord(timeStr[1])
            timeStr = timeStr[2:]
        return time


class Sender(Thread):
    
    def __init__(self):
        self.send = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.packet = ICMPPacket()
        self.packet.source = "10.179.11.198"
        self.packet.destination = "173.194.113.191"
        self.packet.ttl = 1
        super(Sender, self).__init__()
    
    def run(self):
        sequence = 0
        while self.send:
            sequence = sequence + 1
            if not (sequence % 3):
                self.packet.ttl = self.packet.ttl + 1
            self.packet.icmpExtraHeader = "\x08\x08" + chr((sequence >> 8) % 256) + chr(sequence % 256)
            self.packet.icmpMessage = "\x4e\x69\x73\x68\x61\x6e\x74\x2e" + self.getTimeStamp(int(time() * 1000))
            self.packet.makePacket()
            self.sendPacket(self.packet)
            sleep(1)
        
        self.socket.close()
    
    def sendPacket(self, packet):
        self.socket.sendto(packet.data,(packet.destination,0))
    
    def getTimeStamp(self, time):
        timeStr = ""
        while time != 0:
            timepart = time % pow(2,16)
            timeStr = chr((timepart >> 8) % 256) + chr(timepart % 256) + timeStr
            time = time / pow(2,16)
        return timeStr

s = Sender()
s.start()

r = Receiver()
r.start()

while True:
    line = raw_input()
    r.listen = False
    s.send = False
    break

#q = Packet(p.data)
#q.parsePacket()
#q.showPacketDetails()
#print packet.encode("hex")
#p = Packet("10.179.11.198", "10.179.11.75", "\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41")
