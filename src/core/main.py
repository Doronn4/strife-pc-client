import os
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
import wx.lib.inspection
from src.handlers.file_handler import FileHandler
import base64


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
    KeysManager.add_key(chat_id, group_key)
    wx.CallAfter(pub.sendMessage, 'added_to_group', group_name=group_name, chat_id=chat_id)


def handle_friend_add_answer(message):
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'friend_answer', is_valid=is_valid)


def handle_friend_request(message):
    sender_username = message['sender_username']
    is_silent = message['is_silent']
    wx.CallAfter(pub.sendMessage, 'friend_request', adder_username=sender_username, is_silent=is_silent)


def handle_text_message(message):
    sender = message['sender']
    chat_id = message['chat_id']
    raw_message = message['message']
    wx.CallAfter(pub.sendMessage, 'text_message', sender=sender, chat_id=chat_id, raw_message=raw_message)


def handle_user_pic(message):
    username = message['pfp_username']
    contents = base64.b64decode(message['image_contents'])
    wx.CallAfter(pub.sendMessage, 'user_pic', contents=contents, username=username)


def handle_friend_added(message):
    friend_username = message['friend_username']
    friends_key = message['friends_key']
    chat_id = message['chat_id']
    wx.CallAfter(pub.sendMessage, 'friend_added', friend_username=friend_username, friends_key=friends_key,
                 chat_id=chat_id)


def update_chats(message):
    chats_names = message['chats_names']
    if type(chats_names) != list:
        chats_names = [chats_names]

    chats_ids = message['chats_ids']
    if type(chats_ids) != list:
        chats_ids = [chats_ids]

    chats = zip(chats_ids, chats_names)
    wx.CallAfter(pub.sendMessage, 'chats_list', chats=chats)


approve_reject_dict = {
    1: handle_register_ans,
    2: handle_login_ans,
    3: handle_friend_add_answer
}

general_dict = {
    'friend_request': handle_friend_request,
    'added_to_group': handle_added_to_group,
    'chats_list': update_chats,
    # 'group_members': update_group_members,
    # 'user_status': update_user_status,
    'friend_added': handle_friend_added
    # 'text_message': text_message,
    # 'file_description': file_desc,
    # 'file_in_chat': file_received,
    # 'user_profile_picture': update_user_pic
}

chats_dict = {
    'text_message': handle_text_message
}

files_dict = {
    'user_profile_picture': handle_user_pic,
    'file_in_chat': None
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

        if message['opname'] == 'approve_reject':
            if message['function_opcode'] in approve_reject_dict.keys():
                approve_reject_dict[message['function_opcode']](message)

        # Check if the name of the operation is in the dict of functions
        elif message['opname'] in general_dict.keys():
            # Call the function according to the operation
            general_dict[message['opname']](message)


def handle_chats_messages(com, q):
    """
        Handle chats messages incoming from the server
        """
    while True:
        # Take the data from the queue
        data = q.get()
        # Un-protocol the message from the server
        message = Protocol.unprotocol_msg("chat", data)

        if message['opname'] == 'approve_reject':
            if message['function_opcode'] in approve_reject_dict.keys():
                approve_reject_dict[message['function_opcode']](message)

        # Check if the name of the operation is in the dict of functions
        elif message['opname'] in chats_dict.keys():
            # Call the function according to the operation
            chats_dict[message['opname']](message)


def handle_files_messages(com, q):
    while True:
        # Take the data from the queue
        data = q.get()
        if type(data) != str:
            data = data.decode('UTF-8')
        # Un-protocol the message from the server
        message = Protocol.unprotocol_msg("files", data)

        if message['opname'] == 'approve_reject':
            if message['function_opcode'] in approve_reject_dict.keys():
                approve_reject_dict[message['function_opcode']](message)

        # Check if the name of the operation is in the dict of functions
        elif message['opname'] in files_dict.keys() or True:
            # Call the function according to the operation
            files_dict[message['opname']](message)


def main():
    general_queue = queue.Queue()
    general_com = ClientCom(1000, config.server_ip, general_queue)
    threading.Thread(target=handle_general_messages, args=(general_com, general_queue,)).start()

    chats_queue = queue.Queue()
    chats_com = ClientCom(2000, config.server_ip, chats_queue, com_type='chats')
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue,)).start()

    files_queue = queue.Queue()
    files_com = ClientCom(3000, config.server_ip, files_queue, com_type='files')
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue,)).start()

    # Wait for the connection to the server
    while not general_com.running:
        pass

    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))
    KeysManager.initialize(str(wd) + '\\keys')
    FileHandler.initialize(str(wd) + '\\files')

    app = wx.App()
    main_frame = MainFrame(parent=None, title='Strife', general_com=general_com,
                           chats_com=chats_com, files_com=files_com)
    main_frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
