import socket

HOST="127.0.0.1"
PORT=7007
MAXBYTES=65535

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"Socket is listening at {sock.getsockname()}...")
        conn, ret_addr=sock.accept()
        if conn:
            print(f"Connected to {ret_addr}")
            while True:
                received_bytes=conn.recv(MAXBYTES)
                received_msg=received_bytes.decode().strip()
                if not received_msg:
                    print("Connection with the client closing...")
                    break
                print(f"Received {received_msg}")
                conn.send(received_msg.encode())

if __name__=="__main__":
    server()