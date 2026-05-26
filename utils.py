from shared_dictionaries import *
from constants import *

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