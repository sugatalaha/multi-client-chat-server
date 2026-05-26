from shared_dictionaries import *
from utils import broadcast_message

def protocol_parser(message):
    data=message.strip().split(":", 2)
    command=data[0].strip()
    argument=data[1].strip()
    if len(data)>2:
        payload=data[2]
    else:
        payload=""
    return command, argument, payload

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
                conn.sendall(f"system: ERR {receiver_name} not in chat!\n")
        else:
            conn.sendall(f"system: ERR Use # for chat-room or @ for private messaging!\n")
        
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