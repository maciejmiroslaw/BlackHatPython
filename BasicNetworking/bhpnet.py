import sys
import socket
import getopt
import threading
import subprocess

#Global Variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("                         BHPNET                                  ")
    print()
    print("        Usage: bhpnet.py -t target_host -p port")
    print("-l --listen              - listening on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run - Executes given file when recieves connection")
    print("-c --command             - Init shell")
    print("-u --upload=destination  - When connection is recieved, sens file and saves it in destination")
    print()

def client_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        print(f"Connected: {target}:{port}")
        buffer = sys.stdin.read()
        if len(buffer):
            client.sendall(buffer.encode())
        while True:
            recv_len = 1
            response = b""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response.decode(),end="")

            buffer = sys.stdin.read()
            client.sendall(buffer.encode())
    except:
        print("Exception. Closing")
        client.close()

def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)
        print(f"Created server socket on {target}:{port}")
        while True:
            client_sock, addr = server.accept()
            print(f"Client connected: {addr[0]}:{addr[1]}")
            client_thread = threading.Thread(target=client_handler, args=(client_sock,))
            client_thread.start()
    except KeyboardInterrupt:
        server.close()

def run_command(command):
    command = command.rstrip("\n")
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Command did not execute\r\n"
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command
    if len(upload_destination):
        file_buffer = b""
        while b"\\r\\n" not in file_buffer:
            data = client_socket.recv(1024)
            file_buffer += data
        try:
            fd = open(upload_destination, "wb")
            fd.write(file_buffer)
            fd.close()
            client_socket.sendall(f"File saved in {upload_destination}".encode())
        except:
            client_socket.sendall(f"Failure while saving file in {upload_destination}".encode())
        
    if len(execute):
        output = run_command(execute)
        client_socket.sendall(output)

    if command:
        while True:
            #client_socket.sendall("<BHP:#> ".encode())
            cmd_buff = b""
            cmd_buff = client_socket.recv(1024)
            response = b"<BHP:#> "
            response += run_command(cmd_buff)
            client_socket.sendall(response)
    


def main():
    global listen
    global command
    global upload
    global execute
    global command
    global upload_destination
    global target
    global port

    if not len(sys.argv[1:]):
        usage()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
        ["help", "listen", "execute", "target", "port", "command", "upload"])
        print(f"opts: {opts}, args: {args}")
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload = True
            upload_destination = a
        else:
            assert False, "Unrecognized option"
        
    if not listen and len(target) and port > 0:
        client_sender()
    
    if listen:
        server_loop()

if __name__ == "__main__":
    main()
    