import time

from code.core.client_com import ClientCom
from code.core.client_protocol import Protocol
import threading
import queue


def handle_register(com, params):
    print(params)

general_dict = {}
general_dict['register'] = handle_register

general_opcodes = {
    'register': 1,
    'sign_in': 2,
    'add_friend': 3,
    'create_group': 4,
    'start_voice': 5,
    'start_video': 6,
    'change_username': 7,
    'change_status': 8,
    'change_password': 9,
    'get_chat_history': 10,
    'request_file': 11,
    'remove_friend': 12,
    'join_voice': 13,
    'join_video': 14,
    'add_group_member': 15,
    'request_group_members': 16,
    'request_user_picture': 17,
    'request_user_status': 18,
    'request_chats': 19
}


def handle_general_message(com, queue):
    while True:
        data = queue.get()
        msg = Protocol.unprotocol_msg("general", data)
        print(msg)
        if msg['opname'] in general_dict.keys():
            general_dict[msg['opname']](com, msg)


if __name__ == '__main__':
    general_queue = queue.Queue()
    general_com = ClientCom(1000, '127.0.0.1', general_queue)

    threading.Thread(target=handle_general_message, args=(general_com, general_queue,)).start()

    while not general_com.running:
        pass

    msg = Protocol.register("itamarsss", "12345")
    general_com.send_data(msg)

    msg = Protocol.sign_in("itamarsss", "12345")
    general_com.send_data(msg)

    msg = Protocol.create_group("dorons squad")
    general_com.send_data(msg)
