import socket
import sys
import select

IP_CONNECT="127.0.0.1"
PORT_CONNECT=7007
BUFFER_SIZE=65535

buffer=""

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
                    received_message=received_bytes.decode()
                    if received_message==None:
                        break
                    global buffer
                    buffer+=received_message
                    if "\n" in buffer:
                        received_message, buffer=buffer.split("\n", 1)
                    print(f"Recv: {received_message}")
                else:
                    command=sys.stdin.readline()
                    if command.strip().lower()=="quit":
                        print("Connection closing...")
                        break_connection=True
                        break
                    else:
                        data=command
                        sock.sendall(data.encode())
            
if __name__=="__main__":
    client()