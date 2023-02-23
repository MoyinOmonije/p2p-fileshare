import os
import socket
#import threading

#IP = socket.gethostbyname(socket.gethostname()) #for local operations
# '196.24.174.164' = Andreas's public IP

#IP = '196.24.174.164'
IP = '196.24.168.229'
PORT = 4466
ADDR = (IP, PORT)

SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
CLIENT_DATA_PATH = "downloads"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #
    #client.connect(ADDR) #client connects to server
    client.connect(ADDR)
    
    while True:
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "OK":
            print(f"{msg}")
        
        elif cmd == "DISCONNECTED":
             print(f"{msg}")
             break

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))


        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        
        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))

        elif cmd == "UPLOAD":
            ## UPLOAD client_data/file  
            path = data[1]
            with open(f"{path}", "r") as f: #read the file path
                text = f.read()

            ## [client_data, data.txt]
            filename = path.split("/")[-1]
            send_data = f"{cmd}@{filename}@{text}"
            client.send(send_data.encode(FORMAT))

            key = ""
            prompt = client.recv(SIZE).decode(FORMAT)
            print(prompt)
            protectionlvl = input("> ")
            protectionlvl = protectionlvl.strip()

            if(protectionlvl == "o"):
                key = "n/a"
            elif(protectionlvl == "p"):   
                key = input("> ")
                key = key.strip()
            
            client.send(f"{protectionlvl}@{key}".encode(FORMAT))

            
            
            





        elif cmd == "DOWNLOAD":
            send_data = f"{cmd}@{data[1]}"
            client.send(send_data.encode(FORMAT))
            inputkey = ""

            accesslevel = client.recv(SIZE).decode(FORMAT) #receiving p level
            if(accesslevel.strip() == "p"):
                print("This file is protected. Please enter the key.")
                inputkey = input("> ")
                

            elif(accesslevel.strip() == "o"):
                print("anything")
                inputkey = "n/a"

                
            inputkey = inputkey.strip()
            client.send(inputkey.encode(FORMAT))
        
            #client.send(inputkey.encode(FORMAT))
            data1 = client.recv(SIZE).decode(FORMAT)
            data1 = data1.split("@")

            name = data1[1]
            text = data1[2]

            filepath = os.path.join(CLIENT_DATA_PATH, name)
            with open(filepath, "w") as f:
                f.write(text)
            f.close()

        
            

            

        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))


    print("Disconnected from the server")
    client.close()    

if __name__=="__main__":
    main()
    