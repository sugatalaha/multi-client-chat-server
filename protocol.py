from shared_dictionaries import *
from constants import *

def protocol_parser(message):
    data=message.strip().split(":", 2)
    command=data[0].strip()
    if len(data)>1:
        argument=data[1].strip()
        if len(data)>2:
            payload=data[2]
        else:
            payload=""
    else:
        argument=""
        payload=""
    return command, argument, payload

def broadcast_message(conn, message):
    message=message.encode()
    for connection in connections.values():
        if connection != conn:
            connection.sendall(message)

def collect_message(conn):
    while True:
        received_bytes=conn.recv(MAXBYTES)
        received_msg=received_bytes.decode()
        if not received_msg:
            return None
        with lock_buffer:
            if conn not in buffer:
                buffer[conn]=""
            buffer[conn]+=received_msg
            if "\n" in buffer[conn]:
                total_message, remaining=buffer[conn].split("\n", 1)
                buffer[conn]=remaining
                break
    return total_message

def handle_create(conn, command, argument, name, payload=None):
    if command=="/create":
        if argument[0]!='#':
            conn.sendall("Room name must start with #\n".encode())
        else:
            with lock_chat_rooms:
                chat_rooms[argument]=[]
                chat_rooms[argument].append(conn)
                with lock_user_linked_room:
                    user_linked_room.get(name, []).append(argument)
            broadcast_string="system: available chat-rooms:-"
            for chat_room_name in chat_rooms.keys():
                broadcast_string+=f"{chat_room_name}\t"
        broadcast_message(conn, f"{broadcast_string}\n")

def handle_join(conn, command, argument, name, payload=None):
    if command=="/join":
        if argument not in chat_rooms:
            conn.sendall(f"system: ERR Invalid chat room {argument}\n".encode())
        else:
            for connection in chat_rooms[argument]:
                connection.sendall(f"system: {name} has joined chat room {argument}!\n".encode())
            with lock_chat_rooms:
                chat_rooms[argument].append(conn)
                with lock_user_linked_room:
                    if name not in user_linked_room:
                        user_linked_room[name]=[]
                    user_linked_room[name].append(argument)

def handle_msg(conn, command, argument, name, payload):
    if command=="/msg":
        if argument[0]=="#":
            if argument in chat_rooms:
                if argument in user_linked_room.get(name, []):
                    for connection in chat_rooms[argument]:
                        if connection!=conn:
                            connection.sendall(f"{name}:[in {argument}] {payload}\n".encode())
                else:
                    conn.sendall(f"system: ERR You are not part of the room {argument}!\n".encode())
            else:
                conn.sendall(f"system: ERR Invalid chat room {argument}\n".encode())
        elif argument[0]=="@":
            receiver_name=argument[1:]
            if receiver_name in connections:
                connections[receiver_name].sendall(f"{name}: [private] {payload}\n".encode())
            else:
                conn.sendall(f"system: ERR {receiver_name} not in chat!\n".encode())
        else:
            conn.sendall(f"system: ERR Use # for chat-room or @ for private messaging!\n".encode())
        
def handle_leave(conn, command, argument, name, payload):
    if command=="/leave":
        if argument[0]=="#":
            if argument in chat_rooms:
                if name in user_linked_room and argument in user_linked_room.get(name, []):
                    for connection in chat_rooms[argument]:
                        if connection!=conn:
                            connection.sendall(f"system: {name} left the room!\n".encode())
                    with lock_chat_rooms:
                        chat_rooms[argument].remove(conn)
                        with lock_user_linked_room:
                            user_linked_room[name].remove(argument)
                else:
                    conn.sendall(f"system: ERR You are not part of the room {argument}!\n".encode())
            else:
                conn.sendall(f"system: ERR Invalid chat room {argument}!\n".encode())
        else:
            conn.sendall(f"system: ERR Use # followed by the chat room name\n".encode())

def handle_who(conn, command, argument=None, name=None, payload=None):
    if command=="/who":
        active_names="Usernames for active connections: "
        for active_name in connections.keys():
            active_names+=f"{active_name}\t"
        conn.sendall(f"{active_names}\n".encode())

def handle_list(conn, command, argument=None, name=None, payload=None):
    if command=="/list":
        rooms="Available rooms:\t"
        for room_name in chat_rooms.keys():
            rooms+=f"{room_name}\t"
        conn.sendall(f"{rooms}\n".encode())
        
COMMAND={
    "/create":handle_create,
    "/join":handle_join,
    "/msg":handle_msg,
    "/leave":handle_leave,
    "/who":handle_who,
    "/list":handle_list
}