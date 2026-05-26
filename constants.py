from protocol import *

HOST="127.0.0.1"
PORT=7007
MAXBYTES=65535
COMMAND={
    "/create":handle_create,
    "/join":handle_join,
    "/msg":handle_msg,
    "/leave":handle_leave
}