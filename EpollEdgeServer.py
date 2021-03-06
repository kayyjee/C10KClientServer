'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
--  SOURCE FILE:    EpollEdgeServer-Testing.py - A simple echo server using the edge triggered interface of the epoll API
--
--  PROGRAM:        Select method server using epoll edge-triggered
--                  python epollSelectServer.py
--
--  FUNCTIONS:      run(hostIP, port), close(epoll, serversocket, counter, dataTotal), getTime()
--
--  DATE:           February 10, 2015
--
--  REVISIONS:      February 18, 2015
--
--  DESIGNERS:      Kyle Gilles
--
--  PROGRAMMERS:    Kyle Gilles, Justin Tom
--
--  NOTES:
--  The program will accept TCP connections from client machines.
--  The program will read data from the client socket and simply echo it back.
--  Design is a simple, single-threaded server using non-blocking, edge-triggered
--  I/O to handle simultaneous inbound connections. 
--  The program will also keep a log file of the number of connections and all data being echoed.
--  This program is built for performance and does not output clients connected or log information such as amount of data transferred.
--  Test with accompanying client application: echoClient.py
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#!/usr/bin/env python
import socket
import select
import thread
import datetime
import time 


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
--  FUNCTION
--  Name:       run
--  Developer:  Kyle Gilles, Justin Tom
--  Created On: Feb. 10, 2015
--  Parameters:
--      hostIP
--          the IP address of the host
--      port
--          the port to listen on
--  Return Values:
--      none
--  Description:
--      Listens on the specified socket for incoming data, sets a counter for connected clientSocket
--      and echoes back the received data.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''  

def run(hostIP, port):
    running = 1
    counter = 0
    bufferSize = 1024
    #Maintain amount of data sent to and from server
    dataTotal = 0
    #Create an epoll object
    epoll = select.epoll()
    #The connection dictionary maps file descriptors (integers) to their corresponding network connection objects.
    requests = {}
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    #Register interest in read events on the server socket. A read event will occur any time the server socket accepts a socket connection.
    epoll.register(serversocket, select.EPOLLIN | select.EPOLLET)
    requests.update({serversocket.fileno(): serversocket})
    #This method allows a bind() to occur even if a program was recently bound to the port.
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((hostIP, port))
    #The listen backlog queue size
    serversocket.listen(10000)
    #Since sockets are blocking by default, this is necessary to use non-blocking (asynchronous) mode.
    serversocket.setblocking(0)

    
    
    try:
        
        while running:
            events = epoll.poll(-1)
            for fileno, event in events:
                # If a socket connection has been created
                if fileno == serversocket.fileno(): 
                    while 1: 
                        try: 
                            clientConnection, clientAddress = serversocket.accept()
                            counter +=1
                            #Set client connection to non blocking
                            clientConnection.setblocking(0)
                            requests.update({clientConnection.fileno(): clientConnection})
                            #Register EPOLLIN interest.
                            epoll.register(clientConnection, select.EPOLLIN | select.EPOLLET)
                            #If a read event occured, get client data
                            print (str(clientAddress) + " : " + " Just Connected. \n Currently connected clients: " + str(counter) + "\n")
                            text_file.write(str(clientAddress) + " : " + " Just Connected. \n Currently connected clients: " + str(counter) + "\n")
                        except: 
                            break
                elif event & select.EPOLLIN:
                    clientConnection = requests.get(fileno)
                    # Send client data back 
                    try:
                        data = clientConnection.recv(bufferSize)
                        #Get client IP and port
                        clientIP, clientSocket = clientConnection.getpeername()
                        dataSize = len(data)
                        #Add data of client message to total data
                        dataTotal += dataSize
                        #Log data received
                        text_file.write(str(getTime()) + " - Size of data received (" + clientIP + ":" + str(clientSocket) + ") = " + str(dataSize) + '\n')
                        clientConnection.send(data)
                    except:
                        pass

    # Handle a keyboard disconnect.
    except KeyboardInterrupt:
        print ("\nA keyboardInterruption has occured.")
        close(epoll, serversocket, counter, dataTotal)
    
    except Exception,e:
        print ("Unknown Error has occured." + str(e))
        close(epoll, serversocket, counter, dataTotal)

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
--  FUNCTION
--  Name:       close
--  Developer:  Kyle Gilles, Justin Tom
--  Created On: Feb. 10, 2015
--  Parameters:
--      epoll
--          Required to pass the variable to the next function
--      serversocket
--          Required to pass the variable to the next function
--  Return Values:
--      none
--  Description:
--    Cleans up and closes the epoll objects, and sockets as well as closing the log text file.
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''        
                
def close(epoll, serversocket, counter, dataTotal):
    print("\nClosing the server...")
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()            

    text_file.write("\n\nTotal number of connections: " + str(counter))
    text_file.write("Total amount of data transfered: " + str(dataTotal))
    text_file.close()

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
--  FUNCTION
--  Name:       getTime
--  Developer:  Justin Tom
--  Created On: Feb. 18, 2015
--  Parameters:
--      none
--  Return Values:
--      timeStamp
--          The current time of when the function was called
--  Description:
--    Returns the current time of when the function was called in a Y-M-D H:M:S format
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''  
def getTime():
    ts = time.time()
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
    return timeStamp         

 
if __name__=='__main__':
    hostIP = raw_input('Enter your host IP \n')
    port = int(input('What port would you like to use?\n'))

    #Create and initialize the text file with the date in the filename in the logfiles directory
    text_file = open("./Logfiles/" + str(getTime()) + "_EpollServerLog.txt", "w")

    run(hostIP, port)