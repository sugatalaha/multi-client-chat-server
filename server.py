import socket
import threading
from shared_dictionaries import *
from protocol import COMMAND, collect_message, protocol_parser
from constants import *

def handle_client(name, conn):
    while True:
        received_msg=collect_message(conn)
        if received_msg==None:
            with lock_connections:
                for _, connection in connections.items():
                    if connection !=conn:
                        connection.sendall(f"system:{name} has disconnected!\n".encode())
                del connections[name]
                with lock_user_linked_room:
                    for chat_room_name in user_linked_room.get(name, []):
                        with lock_chat_rooms:
                            chat_rooms[chat_room_name].remove(conn) 
                    if name in user_linked_room:
                        del user_linked_room[name]
            break
        else:
            command, argument, payload=protocol_parser(received_msg)
            function_execute=COMMAND.get(command)
            if function_execute:
                function_execute(conn, command, argument, name, payload)
            else:
                conn.sendall(f"system: ERR Invalid command!\n")

                        
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
                    conn.sendall("system: ERR Need name for logging user...\n".encode())
                else:
                    conn.sendall(f"system:Hi, {name_val}\n".encode())
                    with lock_connections:
                        for connection in connections.values():
                            connection.sendall(f"system: {name_val} has joined the chat!\n".encode())
                        connections[name_val]=conn
                    threading.Thread(None, handle_client,None, [name_val, conn]).start()

if __name__=="__main__":
    server()