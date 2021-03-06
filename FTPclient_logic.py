import socket
import os

isLoggedIn=False

class clientLogic():
    def __init__(self, servIP, servPort):
        self.locIP = socket.gethostbyname(socket.gethostname())

        # make command connection with server
        self.servIP = servIP
        if servPort != '' and servPort != 'Port':
            self.servPort = int(servPort)
        else:
            self.servPort = 21
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSock.connect((self.servIP, self.servPort))

        # set default values
        self.binaryFile = False
        self.passive = True
        self.passiveServerPort = ''
        self.passiveServerIP = ''
        self.baseDirectory = os.path.abspath('./clientDirectory')
        self.calledPortPasv = False
        self.doneSending = False
        self.doneReceiving = False

    def getReply(self):
        self.reply = self.clientSock.recv(1024)
        print 'Response:', self.reply
        print ("")

    # AUTHORED BY SASHA BERKOWITZ ------------------------------------------------

# ACCESS CONTROL COMMANDS 

    def USER(self, username):
        # send username to server

        self.clientSock.send('USER '+ username + '\r\n')
        self.getReply()

    def PASS(self, password):
        # send password to server for account authentication

        self.clientSock.send('PASS '+password + '\r\n')
        self.getReply()

    def CWD(self, directory):
        # tell server which directory you want to change to 

        self.clientSock.send('CWD ' + directory + '\r\n')
        self.getReply()
    
    def CDUP(self):
        # tell the server to move up one directory

        self.clientSock.send('CDUP\r\n')
        self.getReply()

    def QUIT(self):
        # tell the server to close the client connection

        self.clientSock.send('QUIT\r\n')
        self.getReply()
                
        if self.reply[:2] == '221':
            self.clientSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.clientSock.close()
    #-----------------------------------------------------------------------------

# TRANSFER PARAMETER COMMANDS 

    # AUTHORED BY LARA TIMM ######################################################
    def PORT(self, ipAddr, port):
        # specifies and sets the address/port to be used in the data connection

        IPChunks = ipAddr.split('.')
        byteU = int(port / 256)         # convert port to base 2
        byteL = port % 256

        connectionString = '%s,%i,%i' % (','.join(IPChunks[:4]), byteU, byteL)
        self.passive = False

        # create and listen on port for data connection from server
        self.activeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.activeSocket.bind((ipAddr, port))
        self.activeSocket.listen(1)
        self.clientSock.send('PORT '+ connectionString +'\r\n')

        print 'Port connection opened at address %s:%u\n' % (ipAddr, port)

        self.calledPortPasv = True
        self.getReply()

    def PASV(self):
        # sends a request to server to listen on a port (other than default), and stores 
        #      the resultant reply for opening data connection

        self.clientSock.send('PASV\r\n')

        reply = self.clientSock.recv(1024)        
        print 'Response:', reply
        if reply[0] == '5':         # if the PASV command fails don't carry on
            return
        openBracketIndex = reply.find('(')
        closeBracketIndex = reply.find(')')

        # recreate the server address from the reply
        connectionString = reply[openBracketIndex+1:-(len(reply) - closeBracketIndex)]
        rec = connectionString.split(',')
        self.passiveServerIP = '.'.join(rec[:4])

        # recreate the passive server port from the reply
        byteU = int(rec[4])
        byteL = int(rec[5])
        self.passiveServerPort = 256*byteU + byteL

        print 'Connecting to server address %s:%u\n' % (self.passiveServerIP, self.passiveServerPort)

        self.calledPortPasv = True
        self.passive = True
    ##############################################################################

    # AUTHORED BY SASHA BERKOWITZ ------------------------------------------------
    def TYPE(self, fileName):
        # send the server the type code for the data being transferred

        if fileName.find('.') != -1:     
            if fileName.find('.txt') != -1 or \
                fileName.find('.html') != -1 or \
                fileName.find('.pl') != -1 or \
                fileName.find('.cgi') != -1:

                self.binaryFile = False
                self.clientSock.send('TYPE A\r\n')
                self.getReply()
            else:
                self.binaryFile = True
                self.clientSock.send('TYPE I\r\n')
                self.getReply()
                    
        else:
            print 'Specified file type not recognised'
            return

    def STRU(self, structureCode):
        # send file structure to the server

        self.clientSock.send('STRU '+structureCode +'\r\n')
        self.getReply()

    def MODE(self, transferMode):
        # send data transmission mode to server

        self.clientSock.send('MODE '+transferMode +'\r\n')
        self.getReply()

    #-----------------------------------------------------------------------------

# SERVICE COMMANDS

    # AUTHORED BY LARA TIMM ######################################################
    def RETR(self, fileName):
        # receive a copy file over data connection
        self.doneReceiving = False
    
        # send name of file to retrieve to server
        self.clientSock.send('RETR '+fileName +'\r\n')

        # if a data connection type isn't specified, get the expected reply from the server
        if not self.calledPortPasv:
            self.getReply()
            return

        self.open_dataSocket()      # open the data socket

        filePath = os.path.join(self.baseDirectory, fileName)
        
        # open the file to write to, open mode depends on the file type set by TYPE command
        if self.binaryFile:
            requestedFile = open(filePath,'wb')
        else :
            requestedFile = open(filePath,'w')

        dataChunk = self.dataStreamSocket.recv(1024)    # receive from the data socket
        while (dataChunk):                              # while more data is being received
            print "Receiving..."
            requestedFile.write(dataChunk)                  # write received data to file
            dataChunk = self.dataStreamSocket.recv(1024)    # receive more data 

        requestedFile.close()
        self.close_dataSocket()
        print "Done Receiving"
        self.doneSending = True

        self.getReply()
        response = self.reply

        # if file transfer was successful then exit otherwise delete the file 
        #       created in the server directory that isn't right
        if response[:3] == '226':
            return
        elif response[:3] == '451' or response[:3] == '550':
            print 'File trainsfer failed'
            if os.path.exists(filePath):
                os.remove(filePath)
        else:
            print 'Unknown transfer error occured'
            self.getReply()

    def STOR(self, fileName):
        # send data across data connection to store as file on server
        
        filePath = os.path.join(self.baseDirectory, fileName)

        # only send a STOR command if the file exists on the client
        if os.path.exists(filePath):
            self.doneSending = False
            self.clientSock.send('STOR '+fileName +'\r\n')
        else:
            print 'File not found'
            return

        if self.calledPortPasv == False:
            self.getReply()
            return

        self.open_dataSocket()
        
        # open the file to read, open mode depends on the file type set by TYPE command
        if self.binaryFile:
            requestedFile = open(filePath,'rb')
        else :
            requestedFile = open(filePath,'r')
            
        fileChunk = requestedFile.read(1024)

        while fileChunk:
            print 'Sending...'
            self.dataStreamSocket.send(fileChunk)
            fileChunk = requestedFile.read(1024)

        requestedFile.close()
        self.close_dataSocket()

        print "Done Sending"
        self.doneSending = True

        self.getReply()

        if self.reply[:3] == '226':
            return
        elif self.reply[:3] == '550':
            print 'File trainsfer failed'
        else:
            print 'Unknown transfer error occured'
            # self.getReply()

    def open_dataSocket(self):
        # passive mode -------------------------------------------------------------------
        if self.passive:
            # open the data socket, connect to server passive port and receive
            self.dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.dataStreamSocket.connect((self.passiveServerIP, self.passiveServerPort))
            self.getReply() 
            
            if not (self.reply[:3] == '150'):    # if the connection is not made, exit the function
                return
        # active mode --------------------------------------------------------------------
        else:
            self.getReply()
            self.dataStreamSocket, addr = self.activeSocket.accept()
    
    def close_dataSocket(self):
        # if not passive close the active socket, close the data stream
        if self.passive == False:
            self.activeSocket.close()
        self.dataStreamSocket.close()
        self.calledPortPasv = False
    ##############################################################################

    # AUTHORED BY SASHA BERKOWITZ ------------------------------------------------
    def DELE(self, fileName):
        # send delete command to server

        self.clientSock.send('DELE ' + fileName +'\r\n')
        self.getReply()
    
    def PWD(self):
        # ask the server to send the current working directory
        self.clientSock.send('PWD\r\n')
        self.getReply()
    #-----------------------------------------------------------------------------

    # AUTHORED BY LARA TIMM ######################################################
    def LIST(self):
        # ask the server for a list of the files in the current working directory
        
        # ensure that the data is sent in ASCII mode
        self.clientSock.send('TYPE A\r\n')      
        reply = self.clientSock.recv(1024)

        self.clientSock.send('LIST\r\n')

        # ensure the server is setup to make a data connection
        if not self.calledPortPasv:
            self.getReply()
            return

        self.open_dataSocket()      # open the data connection

        self.directoryArray = [] 
        directoryItem = self.dataStreamSocket.recv(1024)
        directories = ''

        # while there is incoming data, add the data to a string called directories
        while (directoryItem):
            directories += directoryItem
            directoryItem = self.dataStreamSocket.recv(1024)
        
        # once all the data is recieved, split the string and form an arrat
        self.directoryArray = directories.split('\n')

        # if there is a blank array entry, delete it
        # print out the directories to terminal
        for i in range(0,len(self.directoryArray)):
            print self.directoryArray[i]
            if self.directoryArray[i].strip() == '':
                del self.directoryArray[i]
            
        print 'Number of items in directory:', len(self.directoryArray)
        print "Done Receiving"

        if len(self.directoryArray) == 0:
            print 'Directory empty...'

        self.close_dataSocket()     # close the data connection

        self.getReply()
    ##############################################################################

    # AUTHORED BY SASHA BERKOWITZ ------------------------------------------------
    def MKD(self, dirName):
        # instruct the server to make a directory with the name dirName

        self.clientSock.send('MKD ' + dirName +'\r\n')
        self.getReply()
    
    def RMD(self, dirName):
        # instruct that server to delete the directory with name dirName

        self.clientSock.send('RMD ' + dirName +'\r\n')
        self.getReply()
    
    def NOOP(self):
        # ask the directory to send an okay response
        self.clientSock.send('NOOP\r\n')
        self.getReply()
    #-----------------------------------------------------------------------------
