import socket
import paramiko
import threading
import sys


#using the key from Paramiko demo files
host_key = paramiko.RSAKey(filename='test_rsa.key')

usrnmae = "Mirula"
passwd = "123"

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == usrnmae) and (password == passwd):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print("[OK] Listening for connection...")
    client, addr = sock.accept()
except Exception as E:
    print("[ERR] Listening did not work: ", str(E))
    sys.exit(1)

print("[OK] Got a connection! ", addr[0])

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print("[ERR] Negotiating SSH did not succeed")
    chan = bhSession.accept(20)
    print("[OK] Authenticated!")
    print(chan.recv(1024))
    chan.send("Welcome to bh_ssh!")
    while True:
        try:
            command = input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024).decode() + '\n')
            else:
                chan.send('exit')
                print("Exiting...")
                bhSession.close()
                raise Exception ('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print("[ERR] Got exception: ", str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)

