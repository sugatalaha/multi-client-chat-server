import socket
import threading

HOST="127.0.0.1"
PORT=7007
MAXBYTES=65535

connections={}
lock_connections=threading.Lock()

chat_rooms={}
lock_chat_rooms=threading.Lock()

user_linked_room={}
lock_user_linked_room=threading.Lock()

def protocol_parser(message):
    data=message.strip().split(":", 2)
    command=data[0].strip()
    argument=data[1].strip()
    if len(data)>2:
        payload=data[2]
    else:
        payload=""
    return command, argument, payload

def broadcast_message(conn, message):
    message=message.encode()
    for connection in connections.values():
        if connection != conn:
            connection.send(message)

def handle_client(name, conn):
    while True:
        received_bytes=conn.recv(MAXBYTES)
        received_msg=received_bytes.decode().strip()
        if not received_msg:
            with lock_connections:
                for _, connection in connections.items():
                    if connection !=conn:
                        connection.send(f"system:{name} has disconnected!".encode())
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
            if command=="/create":
                with lock_chat_rooms:
                    chat_rooms[argument]=[]
                    chat_rooms[argument].append(conn)
                    with lock_user_linked_room:
                        user_linked_room.get(name, []).append(argument)
                broadcast_string="system: available chat-rooms"
                for chat_room_name in chat_rooms.keys():
                    broadcast_string+=f"\n{chat_room_name}"
                broadcast_message(conn, broadcast_string)

            elif command=="/join":
                if argument not in chat_rooms:
                    conn.send(f"system: ERR Invalid chat room {argument}".encode())
                else:
                    for connection in chat_rooms[argument]:
                        connection.send(f"system: {name} has joined chat room {argument}!".encode())
                    with lock_chat_rooms:
                        chat_rooms[argument].append(conn)
                        with lock_user_linked_room:
                            if name not in user_linked_room:
                                user_linked_room[name]=[]
                            user_linked_room[name].append(argument)
                            print(name, user_linked_room.get(name, []))
            elif command=="/msg":
                if argument[0]=="#":
                    if argument in chat_rooms:
                        if argument in user_linked_room.get(name, []):
                            for connection in chat_rooms[argument]:
                                if connection!=conn:
                                    connection.send(f"{name}:[in {argument}] {payload}".encode())
                        else:
                            conn.send(f"system: ERR You are not part of the room {argument}!".encode())
                    else:
                        conn.send(f"system: ERR Invalid chat room {argument}".encode())
                elif argument[0]=="@":
                    receiver_name=argument[1:]
                    if receiver_name in connections:
                        connections[receiver_name].send(f"{name}: [private] {payload}".encode())
                    else:
                        conn.send(f"system: ERR {receiver_name} not in chat!")
                else:
                    conn.send(f"system: ERR Use # for chat-room or @ for private messaging!")
            elif command=="/leave":
                if argument[0]=="#":
                    if argument in chat_rooms:
                        if name in user_linked_room and argument in user_linked_room.get(name, []):
                            for connection in chat_rooms[argument]:
                                if connection!=conn:
                                    connection.send(f"system: {name} left the room!".encode())
                            with lock_chat_rooms:
                                chat_rooms[argument].remove(conn)
                                with lock_user_linked_room:
                                    user_linked_room[name].remove(argument)
                        else:
                            conn.send(f"system: ERR You are not part of the room {argument}!".encode())
                    else:
                        conn.send(f"system: ERR Invalid chat room {argument}!".encode())
                else:
                    conn.send(f"system: ERR Use # followed by the chat room name".encode())
            else:
                conn.send(f"system: ERR Invalid command!")

                        
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
                    conn.send("system: ERR Need name for logging user...".encode())
                else:
                    conn.send(f"system:Hi, {name_val}".encode())
                    with lock_connections:
                        for connection in connections.values():
                            connection.send(f"system: {name_val} has joined the chat!".encode())
                        connections[name_val]=conn
                    threading.Thread(None, handle_client,None, [name_val, conn]).start()

if __name__=="__main__":
    server()