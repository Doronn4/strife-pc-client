import os
import time
from pathlib import Path
from src.core.client_com import ClientCom
from src.core.client_protocol import Protocol
import threading
import queue
from src.core.keys_manager import KeysManager
import config
import wx
from pubsub import pub
from src.gui.main_gui import MainFrame


def handle_register_ans(message):
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'register', is_valid=is_valid)


def handle_login_ans(message):
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'login', is_valid=is_valid)


def handle_added_to_group(message):
    group_name = message['group_name']
    chat_id = message['chat_id']
    group_key = message['group_key']
    wx.CallAfter(pub.sendMessage, 'added_to_group', group_name=group_name, chat_id=chat_id)


approve_reject_dict = {
    1: handle_register_ans,
    2: handle_login_ans
}

general_dict = {
    # 'friend_request': friend_request_received,
    'added_to_group': handle_added_to_group
    # 'chats_list': update_chats,
    # 'group_members': update_group_members,
    # 'user_status': update_user_status,
    # 'friend_added': friend_added,
    # 'text_message': text_message,
    # 'file_description': file_desc,
    # 'file_in_chat': file_received,
    # 'user_profile_picture': update_user_pic
}


def handle_general_messages(com, q):
    """
    Handle general messages incoming from the server
    """
    while True:
        # Take the data from the queue
        data = q.get()
        # Un-protocol the message from the server
        message = Protocol.unprotocol_msg("general", data)
        print(message)

        if message['opname'] == 'approve_reject':
            approve_reject_dict[message['function_opcode']](message)

        # Check if the name of the operation is in the dict of functions
        elif message['opname'] in general_dict.keys():
            # Call the function according to the operation
            general_dict[message['opname']](message)


def handle_chats_messages(com, q):
    pass


def handle_files_messages(com, q):
    pass


def main():
    general_queue = queue.Queue()
    general_com = ClientCom(1000, config.server_ip, general_queue)
    threading.Thread(target=handle_general_messages, args=(general_com, general_queue,)).start()

    chats_queue = queue.Queue()
    chats_com = ClientCom(2000, config.server_ip, chats_queue)
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue,)).start()

    files_queue = queue.Queue()
    files_com = ClientCom(3000, config.server_ip, files_queue)
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue,)).start()

    # Wait for the connection to the server
    while not general_com.running:
        pass

    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))
    KeysManager.initialize(str(wd) + 'keys.json')

    app = wx.App()
    main_frame = MainFrame(parent=None, title='Strife', general_com=general_com, chats_com=chats_com, files_com=files_com)
    main_frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
