# Siddhesh Mishra, Jason Hillinger 
# Student ID: 40094356, 40104290
# User ID: si_mish, j_hillin

# Siddhesh Mishra 40094356 and Jason Hillinger 40104290 are the sole authors of this file.

# The purpose of this file is to run the server that will receive requests from clients
# and then send the corresponding repsonse back to that client through a TCP connection

# To compile : python3 Server/server.py 12000 1
# python Server/server.py 12000 1
# Use this command while in the FileTransferService directory

from socket import *
import os
import base64
import sys

# Will print extra information if set to True
DEBUG = False
PORT_INPUT = 12000  #default value for port

#sets the global debug value from the command line
def setDebug():
    global DEBUG
    try:
        DEBUG = sys.argv[2]
    except IndexError:
        print("Debug value not set properly")
        sys.exit()
    if(not(DEBUG == '1' or DEBUG == '0')):
        print("Debug argument must be a 0 or 1")
        sys.exit()
    if(DEBUG == '1'):
        DEBUG = True
        print("DEBUG is set to TRUE")
    if(DEBUG == '0'):
        DEBUG = False
        print("DEBUG is set to FALSE")

#Port numbers range from 0 to 65536, but only ports numbers 0 to 1024 are reserved for privileged services and designated as well-known ports.
def setPort():
    global PORT_INPUT
    try:
        PORT_INPUT = sys.argv[1]
        PORT_INPUT = int(PORT_INPUT)
    except IndexError:
        print("Port value not set properly")
        sys.exit()
    if(PORT_INPUT < 1025 or PORT_INPUT > 65536):
        print("Port value must be between a value between 1025 and 65536")
        sys.exit()
    print("Server Port set to : " + str(PORT_INPUT))

# Prints the text if the var is not empty
def printEmpty(text, var):
    if(var != ''):
        print(text)

# Special print function to print debugging messages
def printd(text):
    if DEBUG:
        # Printing for a request object
        if(type(text) == Request):
            print("Request Received")
            print("Request Binary : " + text.binaryStr)
            print("Opcode : " + text.opcode)
            print("Instruction : " + text.opcode_text)
            printEmpty("File Name Length : " + str(text.fileNameLength) + " bytes",text.fileNameLength)
            printEmpty("File Name : " + text.fileName, text.fileName)
            printEmpty("File Size : " + str(text.fileSize) + " bytes", text.fileSize )
        # Printing for a Response object
        elif(type(text) == Response):
            print("Response Sent")
            print("Response Binary : " + text.serverResponse.decode())
            print("Res-Code : " + text.res_code)
            print("Mnemonic : " + text.mnemonic)
            printEmpty("File Name Length : " + str(text.fileNameLength_base10) + " bytes",text.fileNameLength_base10)
            printEmpty("File Name : " + text.fileName, text.fileName)
            printEmpty("File Size : " + str(text.fileSize_base10) + " bytes", text.fileSize_base10 )
        # Print Regular Text
        else:
            print(text)

def serverSocket():
    host = ''
    port = PORT_INPUT
    serverSocket = socket(AF_INET, SOCK_STREAM) #TCP connection
    serverSocket.bind((host, port))
    serverSocket.listen(1) 
    while True:
        print("Server is running on PORT: " + str(port)) 
        #listening for requests
        clientSocket, clientAddress = serverSocket.accept()
        print("A Connection from: " + str(clientAddress) + " has occured!")
        clientRequest = clientSocket.recv(1000000) 
        print("Server is running on PORT: " + str(port)) 
        request = parseRequestBinary(clientRequest)
        printd(request)
        # print(f"Request = {request}")
        response = processRequest(request)

        # Send response
        if(response != None):
            clientSocket.send(response.serverResponse)
            printd(response)
        else:
            printd("Client disconnected! No response sent!")

        print(f'Closing connection with client address {clientAddress}')
        clientSocket.close()
        print('Socket is listening for new Requests')

class Request:
      def __init__(self, fileName, opcode, fileNameLength, fileSize ='', fileData='', newFileName='', binaryStr = ''):
        self.opcode = opcode
        self.fileName = fileName
        self.binaryStr = binaryStr
        self.opcode_text = "UNKNOWN OPCODE"
        if(opcode == "000"):
            self.opcode_text = "put"
        if(opcode == "001"):
            self.opcode_text = "get"
        if(opcode == "010"):
            self.opcode_text = "change"
            self.newFileName = newFileName
        if(opcode == "011"):
            self.opcode_text = "help"
        self.filenameNoExt, self.ext = os.path.splitext(fileName)
        self.fileNameLength = fileNameLength 
        self.fileSize = fileSize
        self.fileData = fileData

class Response:
    #self.serverResponse should be in a format which is understandable by client
    def __init__(self,res_code,helpData = '',fileData='', fileName = ''):
        self.res_code = res_code
        self.mnemonic = ''
        self.fileNameLength = ''
        self.fileNameLength_base10 = ''
        self.fileData = ''
        self.fileSize = ''
        self.fileSize_base10 = ''
        self.fileName = fileName
        self.serverResponse = (res_code + "00000").encode()
        if(res_code == "001"):
            self.fileData = fileData
            self.fileNameLength_base10 = len(fileName)
            self.fileNameLength = number2base(len(fileName),2,5)
            self.fileSize =  number2base(len(fileData),2,32) #should be 4 bytes long, so 32 bits
            self.fileSize_base10 = len(fileData)
            self.serverResponse = (res_code + self.fileNameLength + fileName + self.fileSize +fileData).encode()
        if(res_code == "110"):
            helpText = "put get change help bye"
            helpLength = number2base(len(helpText),2,5)
            self.serverResponse = ("110" + helpLength + helpText).encode()
        # Setting Mnemonic according to PDFs description (used for debug printing)
        if(res_code == "000"):
            self.mnemonic = 'Response for correct put request and correct change request'
        if(res_code == '001'):
            self.mnemonic = 'Response for correct get request'
        if(res_code == '010'):
            self.mnemonic = 'Error-File Not Found'
        if(res_code == '011'):
            self.mnemonic = 'Error-Unknown request'
        if(res_code =='101'):
            self.mnemonic = 'Response for unsuccessful change'
        if(res_code == '110'):
            self.mnemonic = 'Help-response'
        
# Returns a opcode depending if it fails or if file is successfully updated
def updateFileFromBinary(binaryString,targetfilePath):
    try:
        file = open(targetfilePath,"r+")
    except:
        print("TARGET FILE NOT FOUND IN updateFileFromBinary()")
        return "010"
    try:
        file.write(binaryString)
        print("File write success")
        return "000"
    except:
        print("UNABLE TO WRITE TO FILE " + targetfilePath)
        return "101"

# parses the request sent from the client for the server to understand
def parseRequestBinary(request_binary):
    request_binary = request_binary.decode()
    if(len(request_binary) < 8):
        return
    opcode = request_binary[0:3]
    fileName_length = request_binary[3:8]
    FL_decimal = int(fileName_length, 2)    #file length in decimal. Amount of bytes in file name
    fileName = request_binary[8:FL_decimal + 8] #file name from 8th bit to FL_decimal bit
    match opcode:
        #put
        case "000":
            fileSize = request_binary[FL_decimal + 8 : FL_decimal + 40]
            FS_decimal =  int(fileSize,2)# filesize amount of bytes
            fileData = request_binary[FL_decimal + 40:FL_decimal + 40 +FS_decimal*8]
            return Request(fileName, opcode, FL_decimal, FS_decimal, fileData, binaryStr = request_binary)
        case "001":
            #get
            return Request(fileName,opcode,FL_decimal, binaryStr = request_binary)
        case "010":
            #change
            new_FileName = request_binary[FL_decimal + 16:]
            return Request(fileName,opcode,FL_decimal,newFileName=new_FileName, binaryStr = request_binary)
        case "011":
            return Request(fileName, opcode, FL_decimal, binaryStr = request_binary)
        case _:
            return Request(fileName, opcode,FL_decimal, binaryStr = request_binary)

# Updates the name of a file with a new name
def updateFileName(oldFileName,newFileName):
    oldFileName = os.getcwd() + r"/Server/Files/" + oldFileName
    newFileName = os.getcwd() + r"/Server/Files/" + newFileName
    try:
        os.rename(oldFileName, newFileName)
        return "000"
    except:
        print("unsuccessful change")
        return "101"

def processRequest(req):
    if(req == None):
        return
    if(req.opcode_text == "put"):
        targetfilePath = os.getcwd() + r"/Server/Files/" + req.fileName
        outcome = convertTextToFile(req.fileData,req.fileName)
        #return a success response
        return Response(outcome)
    if(req.opcode_text == "change"):
        outcome = updateFileName(req.fileName, req.newFileName)
        return Response(outcome)
    if(req.opcode_text == "help"):
        return Response('110')
    if(req.opcode_text == "get"):
        targetfilePath = os.getcwd() + r"/Server/Files/" + req.fileName
        fileAsString = convertFileToText(req.fileName)
        if(fileAsString):
            return Response('001',fileData=fileAsString, fileName=req.fileName)
        return Response("010")
    #invalid request
    return Response("011")

#Converts a number to a specific base (mostly used for decimal -> binary)
def number2base(n, b,amountOfBits):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return str(digits[::-1]).replace('[','').replace(', ','').replace(']','').zfill(amountOfBits)

#Converts an existing file into a string to be added to a response or request
def convertFileToText(fileName):
    try:
        currentWorkingDirectory = os.getcwd()
        fullPath = currentWorkingDirectory + r"/Server/Files/" + fileName
        file = open(fullPath,"rb")
        encodedString = str(base64.b64encode(file.read()))[2:]
        return encodedString.replace("'",'')
    except:
        print("file not found CFT")
        return False

#For the client or server to recreate the file with the give text
def convertTextToFile(text,newFileName):
    try:
        currentWorkingDirectory = os.getcwd()
        fullPath = currentWorkingDirectory + r"/Server/Files/" + newFileName
        decodeit = open(fullPath, 'wb')
        decodeit.write(base64.b64decode((text)))
        decodeit.close()
        return "000"
    except:
        print('file not found CTF')
        return "010"

# Returns the size of a file in bytes in binary. The file must be a string
def sizeOfFile(fileAsText,bits):
    return str(number2base(len(fileAsText),2,bits))

# Main
if __name__ == '__main__':
    setPort()
    setDebug()
    serverSocket()