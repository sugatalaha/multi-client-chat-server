import socket

IP_CONNECT="127.0.0.1"
PORT_CONNECT=7007
BUFFER_SIZE=65535

def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP_CONNECT, PORT_CONNECT))
        print("Connected to server...")
        name=str(input("Name: "))
        sock.send(f"name={name.strip()}".encode())
        received_bytes=sock.recv(BUFFER_SIZE)
        print(f"Recv: {received_bytes.decode()}")
        while True:
            command=str(input("Send: "))
            if command.strip().lower()=="quit":
                print("Connection closing...")
                break
            else:
                data=command
                sock.send(data.encode())
                received=sock.recv(BUFFER_SIZE)
                print(f"Recv: {received.decode()}")

if __name__=="__main__":
    client()