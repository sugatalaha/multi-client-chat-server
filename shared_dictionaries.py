import threading

connections={}
lock_connections=threading.Lock()

chat_rooms={}
lock_chat_rooms=threading.Lock()

user_linked_room={}
lock_user_linked_room=threading.Lock()

buffer={}
lock_buffer=threading.Lock()