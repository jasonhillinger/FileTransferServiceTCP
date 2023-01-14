# Siddhesh Mishra, Jason Hillinger 
# Student ID: 40094356, 40104290
# User ID: si_mish, j_hillin

# Siddhesh Mishra 40094356 and Jason Hillinger 40104290 are the sole authors of this file.

# This file is the client side of the socket. The purpose of this file is to run the commands inputted directly by the client.
# This file then formats the request string from the user and sends this request to the server socket. 
# Once a response is received, it is parsed, executed and displayed to the user. 


# To run use the following command
# cd Client
# python3 client.py localhost 12000 0

from socket import *
import pyinputplus as pyip
import os
import sys, getopt
import base64

# Global debug variable 
global dbug


# When running debugger add /Client to lines 350, 409 and 418

# Creating a client socket
def clientSocket(host, port):

    print(f'Connected to server on host: {host} and port {port}')
    print("Session has been established")


    while(True):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        # Get client request
        request = clientInput()
        # Get Final Request string to be sent
        req = getRequestString(request)
        print(f'Dbug is {dbug}')
        if(dbug):
            print(f'request being sent = {req}')

        # check if opcode is bye
        if(req == "bye"):
            print("Client Disconnecting")
            s.close()
            break
        else:
            s.send(req.encode())
            if(dbug):
                print(f'The request has been sent')
            
            # receive files:
            res = s.recv(1000000)
            if(dbug):
                print('The server has sent a response')
            decodedRes = res.decode()
            rescode= checkResCode(decodedRes,request)
            print(rescode)





def clientInput():
    # Getting all inputs from users
    print("Please enter an ID for your request: ")
    clientRequest = pyip.inputCustom(checkFileNameLen)
    # print(f"Final input from user: {clientRequest}")
    if(dbug):
        print(f'The request being made is: {clientRequest}')
    return clientRequest

# --------------------------------------------------Client Input Check---------------------------------------------#         
# Checking if the file name entered by user is less than 31
def checkFileNameLen(clientRequest):
    opcode = checkOpcode(clientRequest)
    byteOp = getOpcode(clientRequest)
    if(opcode == clientRequest):
        fileNameRequest, finalOp = getOnlyFilenames(clientRequest)
        # checking if the opcode is change or bye
        match byteOp:
            case '000':
                # dot split
                fileNameLen = len(fileNameRequest)
                # check if file name len is less than 31 chars
                if(fileNameLen > 31):
                    raise Exception('File name too long')
                else:
                    filename, ext = os.path.splitext(fileNameRequest)
                    filePath =f"{filename}{ext}"
                    clientRequest = f"{finalOp} {filePath}"
                    # Get the file name and its exists
                    fileExsits = getFilePathAndSize(filePath)
                    if(fileExsits):
                        return clientRequest
                    else:
                        raise Exception(f'No file with name {fileNameRequest}')
            # The opcode is get
            case '001':
                fileNameLen = len(fileNameRequest)
                if(fileNameLen > 31):
                    raise Exception('File name too long')
                else:
                    return clientRequest
            # The opcode is change
            case '010':
                # Get lengths of the old and new file 
                oldFilename, oldFilenameExt, newFilename, newFilenameExt = getOldandNewFilenames(fileNameRequest)
                # Aggregate the filename and ext
                oldFile = oldFilename + oldFilenameExt
                newFile = newFilename + newFilenameExt
                oldFileLen = len(oldFile)
                newFileLen = len(newFile)
                # Make sure both file names are 31 chars or less
                if(oldFileLen > 31):
                    raise Exception('Old filename too long')
                elif(newFileLen > 31):
                    raise Exception('Old filename too long')
                # make sure both extentions are the same
                elif(oldFilenameExt != newFilenameExt):
                    raise Exception('Please check the extensions and make sure they are the same')
                else:
                    oldFilePath =f"{oldFilename}{oldFilenameExt}"
                    newFilePath =f"{newFilename}{newFilenameExt}"
                    clientRequest = f"{finalOp} {oldFilePath} {newFilePath}"
                    return clientRequest
            case _:
                return clientRequest

    else:
        raise Exception('Invalid Command')

# Get the binary opcode 
def getOpcode(clientRequest):
    request = clientRequest.split(' ')
    
    opcode = request[0]
    match opcode:
        case 'put':
            bitOp = '000'
        case 'get':
            bitOp = '001'
        case 'change':
            bitOp = '010'
        case 'help':
            bitOp = '011'
        case 'bye':
            return 'bye'
        # set opcode if command is invalid
        case _:
            bitOp = '100'
    return bitOp        

# Checking if the command entered by user is correct
def checkOpcode(request):
    splitRequest = request.split(' ')
    opcode = splitRequest[0]
    match opcode:
        case 'put':
            return request
        case 'get':
            return request
        case 'change':
            return request
        case 'help':
            return request
        case 'bye':
            return request
        case _:
            return request
        #     raise Exception('Invalid command')
 
# Get file name without the op
def getOnlyFilenames(clientRequest):
     # splitting request to take out opcode
    splitRequest = clientRequest.split(' ')
    finalOp = splitRequest[0]
    # removing op code from request
    noOpReq = splitRequest[1:]
    # make the noOpReq list into a string
    fileNameRequest = ' '.join(noOpReq)
    return fileNameRequest, finalOp

# get extension and filename from the req
def getOldandNewFilenames(noOpRequest):
    # oldAndNewFilename is the old File and new file together,
    # newFilenameExt is the extension of the new file 
    oldAndNewFilename, newFilenameExt = os.path.splitext(noOpRequest)
    # fileName1 is the old File name 
    # ext1 is the extension of the oldfile name and the name of the newfilename 
    oldFilename, ext1 = os.path.splitext(oldAndNewFilename)
    # split the spaces in the ext1 to get the oldfilename extension and newFilename
    extSpace = ext1.split(' ')
    # store the old file ext in oldFilenameExt and remove it from the array
    oldFilenameExt = extSpace.pop(0)
    # join the rest of the extSpace array to get the new filename
    newFilename = ' '.join(extSpace)
    
    return oldFilename, oldFilenameExt, newFilename, newFilenameExt

# --------------------------------------------------Client Input Check end---------------------------------------------#         

# --------------------------------------------------Client Request String---------------------------------------------#         

def getRequestString(clientRequest):
    # Getting opcode 
    opcode = getOpcode(clientRequest)
  
    # Getting the filenames without opcode
    noOpRequest, strOp = getOnlyFilenames(clientRequest)
    # Filename length in decimal 
    fileNameLenDec = len(noOpRequest)
    # Get filename length in binary
    fileNameLenBin = bin(fileNameLenDec)[2:]
    match opcode:
        case '000':
            # Get file size
            #fileSize = getFilePathAndSize(noOpRequest)
            fileData = readFiles(noOpRequest)
            fileSize = sizeOfFile(fileData, 32)
            requestStr =f"{opcode}{fileNameLenBin.zfill(5)}{noOpRequest}{fileSize}{fileData}" 
        case '001':
            requestStr =f"{opcode}{fileNameLenBin.zfill(5)}{noOpRequest}"
        case '010':
            # Get lengths of the old and new file 
            oldFilename, oldFilenameExt, newFilename, newFilenameExt = getOldandNewFilenames(noOpRequest)
            # Aggregate the filename and ext
            oldFile = oldFilename + oldFilenameExt
            newFile = newFilename + newFilenameExt
            # Filename length in decimal 
            oldFileLenDec = len(oldFile)
            newFileLenDec = len(newFile)
            # Get old filename length in binary (5 bits)
            oldFileLenBin = bin(oldFileLenDec)[2:]
            # Get new filename length in binary (8bits)
            newFileLenBin = bin(newFileLenDec)[2:]

            requestStr = f"{opcode}{oldFileLenBin.zfill(5)}{oldFile}{newFileLenBin.zfill(8)}{newFile}"
        case '011':
            requestStr = f"{opcode}00000"
        case 'bye':
            requestStr = 'bye'
        case _:
            requestStr = f'{opcode}00000'
        
    return requestStr

# Converts a number to a specific base (mostly used for decimal -> binary)
def number2base(n, b,amountOfBits):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return str(digits[::-1]).replace('[','').replace(', ','').replace(']','').zfill(amountOfBits)

# Returns the size of a file in bytes in binary. The file must be a string
def sizeOfFile(fileAsText,bits):
    return str(number2base(len(fileAsText),2,bits))


# Get file size unused
def getFilePathAndSize(fileName):
    try:
        filePath = checkFilePath(fileName)
        if(filePath):
            fileSize = os.path.getsize(filePath)
            if(dbug):
                print(f"File with name {fileName} has been found")
            fileSizeBin = bin(fileSize)[2:]
            fileSizeBinLen = len(fileSizeBin)
            if(fileSizeBinLen != 32):
                fullFileSize = fileSizeBin.zfill(32)
                return fullFileSize
        else:
            return False
    except:
        return print(f"No file with name {fileName}")

# Read file and return file data
def readFiles(fileNameRequest):
    filePath = checkFilePath(fileNameRequest)

    if(filePath):
        filename, ext = os.path.splitext(fileNameRequest)     

        try:
            # Open file
            imgFile = open(filePath, 'rb')
            if(dbug):
                print(f'Reading file: {filename}')
            data = imgFile.read()
            convertedData = base64.b64encode(data)
            convertedStringData = str(convertedData)[2:].replace("'","")
            imgFile.close()
            return convertedStringData
        except Exception as e:
            print(e)

            


# if get req file already exists, add a number to the file name
def updateFilename(filename):
    fileInPath = checkFilePath(filename)
    getVersionOfFile = filename.split(" ")
    copyInFile = 'Copy' in filename
    if(copyInFile):
        # get the index of copy
        getIndexOfCopy = getVersionOfFile.index('Copy')
        # get array size
        lastIndexOfVersionFile = len(getVersionOfFile)-1
        # Check if the copy is at the end of the array
        if(getIndexOfCopy== lastIndexOfVersionFile):
            newFilename = f"{filename} (2)"      
        else:
            fileVersion = getVersionOfFile[-1]
            currentVersion = fileVersion[fileVersion.find('(')+1:fileVersion.find(')')]
            newVersion = int(currentVersion) + 1
            del getVersionOfFile[lastIndexOfVersionFile]
            filename = ' '.join(getVersionOfFile)
            newFilename = f"{filename} ({newVersion})"
    else:
        newFilename = f"{filename} - Copy"  
    print(newFilename)    
    return newFilename


# Check if filepath exists
def checkFilePath(fileNameRequest):
    # Make the file Path
    filePath = f"./Files/{fileNameRequest}"
    # Check if the path exists 
    filePathExist = os.path.isfile(filePath)
    if(filePathExist):
        return filePath
    else:
        return False
# --------------------------------------------------Parse Reponse end---------------------------------------------#         
def parseServerResponse(decodedRes):
    # Parse the size of the filename
    fileNameLength = decodedRes[3:8]
    # change the fileNameLength from binary to decimal
    fileNameSize = int(fileNameLength,2)
    # Get index of the end of file name
    endFilenameIndex = 8 + fileNameSize
    # Get the filename only from the decoded response
    resFilename = decodedRes[8:endFilenameIndex]
    # Get start index of data
    fileDataStartIndex = endFilenameIndex + 32
    # File data
    fileData = decodedRes[fileDataStartIndex:]
    return resFilename, fileData
# Check response code 
def checkResCode(decodedRes, clientRequest):
    resCode = decodedRes[:3]
    if(dbug):
        print(f'Server response code is: {resCode}')
    reqFilenames, opCode = getOnlyFilenames(clientRequest)
    bitOP = getOpcode(opCode)
    match resCode:
        case '000':
            match bitOP:
                case '000':
                    message = f'{reqFilenames} has been uploaded successfully'
                case _:
                    of, ofext, nf, nfext = getOldandNewFilenames(reqFilenames)
                    message = f'{of}{ofext} has been changed into {nf}{nfext}'
        case '001':
            filename, fileData = parseServerResponse(decodedRes)
            writeFile = convertTextToFile(fileData,filename)
            message = f'{writeFile} has been downloaded successfully'
        case '010':
            message = f'Get Request failed, file not found'
        case '011':
            message = f'Unknown Request, please enter a valid opcode.'
        case '101':
            message = f'Change Request failed, invalid file name[s]'
        case '110':
            message = f'Commands are: {decodedRes[8:]}'
        case _:
            message =f'debug'
    return message
#For the client or server to recreate the file with the give text
def convertTextToFile(fileData,filename):
    try:
        filenameExist = checkFilePath(filename)        
        if(not filenameExist):
            fullPath = f'./Files/{filename}'
            decodeit = open(fullPath, 'wb')
            decodeit.write(base64.b64decode((fileData)))
            decodeit.close()
            return filename
        else:
            fileName, ext = os.path.splitext(filename)
            newFilename = updateFilename(filename)
            newfile = f'{newFilename}{ext}'
            newfullPath = f'./Files/{newfile}'
            decodeit = open(newfullPath, 'wb')
            decodeit.write(base64.b64decode((fileData)))
            decodeit.close()
            return newFilename
    except Exception as e:
        print(e)
        print('file not found CTF')

# --------------------------------------------------Parse Reponse end---------------------------------------------#         
# --------------------------------------------------Sys Args Checks---------------------------------------------#  
# Checking all system arguments
def sysArgCheck(argsv):

    totalArgs = len(argsv)
    if(totalArgs > 4):
        return "Too many arguments"
    else:
        # assign 1 argument to port, host and debug
        host = argsv[1] 
        port = argsv[2]
        dbug = argsv[3]
        print(f'Host = {host}\nport = {port}\ndbug = {dbug}')
        return host, port, dbug 
# --------------------------------------------------Sys Args Checks end---------------------------------------------#  

if __name__ == '__main__':
    try:

        argsv = sys.argv
        host, port, dbug = sysArgCheck(argsv)
        if(dbug == '1'):
            dbug = True
        else:
            dbug = False

        print(f'debug = {dbug}')
    except getopt.GetoptError:
        print ('Wrong system argument commands')
        sys.exit(2)

    clientSocket(host, int(port))