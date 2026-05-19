import socket
import sys
import select

IP_CONNECT="127.0.0.1"
PORT_CONNECT=7007
BUFFER_SIZE=65535

def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((IP_CONNECT, PORT_CONNECT))
        rlist=[sys.stdin, sock]
        print("Connected to server...")
        name=str(input("Name: "))
        sock.send(f"name={name.strip()}".encode())
        break_connection=False
        while not break_connection:
            ready_fds, _, _=select.select(rlist, [], [])
            for source in ready_fds:
                if source==sock:
                    received_bytes=sock.recv(BUFFER_SIZE)
                    print(f"Recv: {received_bytes.decode()}")
                else:
                    command=sys.stdin.readline()
                    if command.strip().lower()=="quit":
                        print("Connection closing...")
                        break_connection=True
                        break
                    else:
                        data=command.strip()
                        sock.send(data.encode())
            
if __name__=="__main__":
    client()