import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print(f"Listening on ip:port: {bind_ip}:{bind_port}")

def handle_client(client_socket):
    request = b""
    while b"\r\n\r\n" not in request:
        #Assumming every message is ending with double CRLF to assure I'm recieving everything.
        request += client_socket.recv(4096)
    print(f"Recieved: {request.decode()}")

    client_socket.send("ACK!\r\n\r\n".encode())
    client_socket.close()

if __name__ == "__main__":

    while True:
        client, addr = server.accept()
        print(f"Connected with: {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

    