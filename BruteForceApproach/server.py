import os
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 4466
ADDR = ('', PORT)

# ADDR = (IP, PORT) #for local operations
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
TXT_LOG_DATA_PATH = "server_data/txt_file_logs"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@") 
        cmd = data[0]
        
        if cmd == "HELP":
            send_data = "OK@"
            send_data += "LIST: List all the files from the sever. \n"
            send_data += "UPLOAD <path>: Upload a file to the server. \n"
            send_data += "DELETE <filename>: Delete a file from the server. \n"
            send_data += "DOWNLOAD <filename>: Download a file from the server. \n"
            send_data += "LOGOUT: Disconnect from the server. \n"
            send_data += "HELP: List all the commands."

            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "LIST":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))


        elif cmd == "UPLOAD":
            name = data[1] #file name
            text = data[2] #file contents

            #prompt client to select protection level of file to be uploaded
            clientprompt = "Select protection level for this file. \nEnter [o] for open or [p] for protected"
            conn.send(clientprompt.encode(FORMAT))

            #receive protection level and key
            clientresponse = conn.recv(SIZE).decode(FORMAT)
            clientresponse = clientresponse.split("@")
            
            accesslevel = clientresponse[0] #protection level (p or o)
            accesskey = clientresponse[1]   #key

            fname = name.split(".")
            flog = fname[0]
            flog = flog+".txt"      
            flogtext = accesslevel+"\n"+accesskey

            flogpath = os.path.join(TXT_LOG_DATA_PATH, flog)
            with open(flogpath, "w") as f:
                f.write(flogtext)

            filepath = os.path.join(SERVER_DATA_PATH, name)
            with open(filepath, "w") as f:
                f.write(text)
            
            send_data = "OK@File uploaded."
            conn.send(send_data.encode(FORMAT))
        

        elif cmd == "DOWNLOAD":
            name = data[1]

            accesskey = ""
            accesslevel = ""

            txtfp = os.path.join(TXT_LOG_DATA_PATH, name)
            with open(txtfp, "r") as f:
                access = f.readline()
                accesslevel = access.strip()
                key = f.readline()
                accesskey = key.strip()


            filepath = os.path.join(SERVER_DATA_PATH, name)
            with open(f"{filepath}", "r") as f: #read the file path
                text = f.read()

            conn.send(accesslevel.encode(FORMAT)) #send protection level

            accessgranted = False
            inputkey = conn.recv(SIZE).decode(FORMAT)

            if(accesslevel.strip() == "p"):

                #inputkey = conn.recv(SIZE).decode(FORMAT)
                inputkey = inputkey.strip()
                if(key == inputkey):
                    accessgranted = True
                    
            elif(accesslevel.strip() == "o"):

                #inputkey = conn.recv(SIZE).decode(FORMAT)
                inputkey = inputkey.strip()
                if(key == inputkey):
                    accessgranted = True
                
                
            if(accessgranted == True):
                send_data = f"{cmd}@{name}@{text}"
                conn.send(send_data.encode(FORMAT))
            
            send_data = "OK@something."
            conn.send(send_data.encode(FORMAT))
            #datam = "OK@File downloaded."
            #conn.send(datam.encode(FORMAT))


        
            




        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty."
            else:
                if filename in files:
                    os.system(f"del {SERVER_DATA_PATH}/{filename}") #rm for linux, del for windows (check how to do on all systems, 42:20)
                    send_data += "File deleted."
                else:
                    send_data += "File not found."
            conn.send(send_data.encode(FORMAT))

    print(f"[DISCONNECTED] {addr} Disconnected")
    conn.close()

def main():
    print("[STARTING] Server is starting.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create tcp server
    server.bind(ADDR)
    server.listen(1)
    print(f"[LISTENING] Server is listening on {IP} : {PORT}.")

    while True:
        conn, addr = server.accept() #server accepts connection for client
        thread = threading.Thread(target= handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count()-1}") 

if __name__=="__main__":
    main()