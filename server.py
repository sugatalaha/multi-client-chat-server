import socket
import threading

HOST="127.0.0.1"
PORT=7007
MAXBYTES=65535

connections=[]

def handle_client(name, conn):
    while True:
        received_bytes=conn.recv(MAXBYTES)
        received_msg=received_bytes.decode().strip()
        if not received_msg:
            for connection in connections:
                if connection !=conn:
                    connection.send(f"system:{name} has left the chatroom!".encode())
            connections.remove(conn)
            break
        for connection in connections:
            if connection!=conn:
                connection.send(f"{name}:{received_msg}".encode())

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        while True:
            sock.listen(5)
            print(f"Socket is listening at {sock.getsockname()}...")
            conn, ret_addr=sock.accept()
            if conn:
                print(f"Connected to {ret_addr}")
                received_name_msg=conn.recv(MAXBYTES)
                name_split_array=received_name_msg.decode().split("=")
                name_key=name_split_array[0]
                name_val=name_split_array[1]
                if name_key!="name":
                    conn.send("system:Need name for logging user...".encode())
                else:
                    conn.send(f"system:Hi, {name_val}".encode())
                    for connection in connections:
                        connection.send(f"system:{name_val} has joined the chatroom!".encode())
                    connections.append(conn)
                    threading.Thread(None, handle_client,None, [name_val, conn]).start()

if __name__=="__main__":
    server()