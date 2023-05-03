import os
import re
from pathlib import Path
import signal
import threading
import queue
import wx
from pubsub import pub
import base64
import sys
import socket
import subprocess
import ipaddress
import wx.lib.inspection

# Add the project folder to PYTHONPATH
project_dir = str(Path(os.path.abspath(__file__)).parent.parent.parent)
sys.path.insert(0, project_dir)

from src.core.cryptions import AESCipher
from src.core.client_com import ClientCom
from src.core.client_protocol import Protocol
from src.core.keys_manager import KeysManager
from src.handlers.file_handler import FileHandler
from src.gui.main_gui import MainFrame
import config


def handle_register_ans(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'register', is_valid=is_valid)


def handle_login_ans(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'login', is_valid=is_valid)


def handle_added_to_group(message):
    """
    :param message: The message received from the server.
    """
    group_name = message['group_name']
    chat_id = message['chat_id']
    group_key = message['group_key']
    KeysManager.add_key(chat_id, group_key)
    wx.CallAfter(pub.sendMessage, 'added_to_group', group_name=group_name, chat_id=chat_id)


def handle_friend_add_answer(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'friend_answer', is_valid=is_valid)


def handle_friend_request(message):
    """
    :param message: The message received from the server.
    """
    sender_username = message['sender_username']
    is_silent = bool(message['is_silent'])
    wx.CallAfter(pub.sendMessage, 'friend_request', adder_username=sender_username, is_silent=is_silent)


def handle_text_message(message):
    """
    :param message: The message received from the server.
    """
    sender = message['sender']
    chat_id = message['chat_id']
    raw_message = message['message']
    wx.CallAfter(pub.sendMessage, 'text_message', sender=sender, chat_id=chat_id, raw_message=raw_message)


def handle_user_pic(message):
    """
    :param message: The message received from the server.
    """
    username = message['pfp_username']
    contents = base64.b64decode(message['image_contents'])
    wx.CallAfter(pub.sendMessage, 'user_pic', contents=contents, username=username)


def handle_friend_added(message):
    """
    :param message: The message received from the server.
    """
    friend_username = message['friend_username']
    friends_key = message['friends_key']
    chat_id = message['chat_id']
    wx.CallAfter(pub.sendMessage, 'friend_added', friend_username=friend_username, friends_key=friends_key,
                 chat_id=chat_id)


def update_chats(message):
    """
    :param message: The message received from the server.
    """
    chats_names = message['chats_names']
    if type(chats_names) != list:
        chats_names = [chats_names]

    chats_ids = message['chats_ids']
    if type(chats_ids) != list:
        chats_ids = [chats_ids]

    chats = [(chats_ids[i], chats_names[i]) for i in range(0, len(chats_ids))]
    wx.CallAfter(pub.sendMessage, 'chats_list', chats=chats)


def update_group_members(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    usernames = message['usernames']
    if type(usernames) != list:
        usernames = [usernames]
    wx.CallAfter(pub.sendMessage, 'group_members', chat_id=chat_id, usernames=usernames)


def update_user_status(message):
    """
    :param message: The message received from the server.
    """
    username = message['username']
    status = message['status']
    wx.CallAfter(pub.sendMessage, 'user_status', username=username, status=status)


def handle_file_description(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    file_name = message['file_name']
    file_size = message['file_size']
    sender = message['sender']
    file_hash = message['file_hash']
    wx.CallAfter(pub.sendMessage, 'file_description', chat_id=chat_id, file_name=file_name,
                 file_size=file_size, sender=sender, file_hash=file_hash)


def handle_file_in_chat(message):
    """
    :param message: The message received from the server.
    """
    # Show a dialog to select the location to save the file
    dialog = wx.FileDialog(None, message="Save file", defaultDir="", defaultFile=message['file_name'],
                           wildcard="All files (*.*)|*.*", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dialog.ShowModal() == wx.ID_OK:
        chat_id = message['chat_id']
        # Get the path of the selected file
        file_path = dialog.GetPath()
        # Decrypt the file contents using the chat key
        file_contents_b64 = AESCipher.decrypt(KeysManager.get_chat_key(chat_id), message['file_contents'])
        # B64 decode the contents
        file_contents = base64.b64decode(file_contents_b64)
        # Save the file using the FileHandler
        FileHandler.save_file(file_contents, file_path)

    dialog.Destroy()


def handle_chat_history(message):
    """
    :param message: The message received from the server.
    """
    if type(message['messages']) != list:
        messages = [message['messages']]
    else:
        messages = message['messages']

    messages_params = []
    for msg in messages:
        msg = base64.b64decode(msg.encode()).decode()
        msg_params = Protocol.unprotocol_msg('chat', msg)
        messages_params.append(msg_params)
    
    wx.CallAfter(pub.sendMessage, 'chat_history', messages=messages_params, chat_id=message['chat_id'])


def handle_voice_info(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    ips = message['ips']
    usernames = message['usernames']

    if type(ips) != list:
        ips = [ips]
        usernames = [usernames]

    wx.CallAfter(pub.sendMessage, 'voice_info', chat_id=chat_id, ips=ips, usernames=usernames)


def handle_video_info(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    ips = message['ips']
    usernames = message['usernames']

    if type(ips) != list:
        ips = [ips]
        usernames = [usernames]

    wx.CallAfter(pub.sendMessage, 'video_info', chat_id=chat_id, ips=ips, usernames=usernames)


def handle_voice_joined(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    ip = message['user_ip']
    username = message['username']

    wx.CallAfter(pub.sendMessage, 'voice_joined', chat_id=chat_id, ip=ip, username=username)


def handle_video_joined(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    ip = message['user_ip']
    username = message['username']

    wx.CallAfter(pub.sendMessage, 'video_joined', chat_id=chat_id, ip=ip, username=username)


def handle_voice_started(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    wx.CallAfter(pub.sendMessage, 'voice_started', chat_id=chat_id)


def handle_video_started(message):
    """
    :param message: The message received from the server.
    """
    chat_id = message['chat_id']
    wx.CallAfter(pub.sendMessage, 'video_started', chat_id=chat_id)


def handle_username_change_ans(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'username_answer', is_valid=is_valid)


def handle_status_change_ans(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'status_answer', is_valid=is_valid)


def handle_password_change_ans(message):
    """
    :param message: The message received from the server.
    """
    is_valid = bool(message['is_approved'])
    wx.CallAfter(pub.sendMessage, 'password_answer', is_valid=is_valid)


def handle_keys(message):
    keys = message['keys']
    chat_ids = message['chat_ids']

    if type(keys) != list:
        keys = [keys]
        chat_ids = [chat_ids]

    wx.CallAfter(pub.sendMessage, 'keys', keys=keys, chat_ids=chat_ids)


# The dictionary that contains the functions to handle the messages of rejection and approval
approve_reject_dict = {
    1: handle_register_ans,
    2: handle_login_ans,
    3: handle_friend_add_answer,
    7: handle_username_change_ans,
    8: handle_status_change_ans,
    9: handle_password_change_ans
}

# The dictionary that contains the functions to handle the general messages of the server
general_dict = {
    'friend_request': handle_friend_request,
    'added_to_group': handle_added_to_group,
    'chats_list': update_chats,
    'group_members': update_group_members,
    'user_status': update_user_status,
    'friend_added': handle_friend_added,
    'voice_call_info': handle_voice_info,
    'video_call_info': handle_video_info,
    'voice_user_joined': handle_voice_joined,
    'video_user_joined': handle_video_joined,
    'voice_call_started': handle_voice_started,
    'video_call_started': handle_video_started,
    'keys': handle_keys
}

# The dictionary that contains the functions to handle the chats messages of the server
chats_dict = {
    'text_message': handle_text_message,
    'file_description': handle_file_description,
    'chat_history': handle_chat_history
}

# The dictionary that contains the functions to handle the files messages of the server
files_dict = {
    'user_profile_picture': handle_user_pic,
    'file_in_chat': handle_file_in_chat
}


def handle_general_messages(com, q):
    """
    Handle general messages incoming from the server
    :param com: The communication object
    :param q: The queue to take the messages from
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
    :param com: The communication object
    :param q: The queue to take the messages from
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
    """
    Handle files messages incoming from the server
    :param com: The communication object
    :param q: The queue to take the messages from
    """

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


def detect_server_locally(server_port: int):
    """
    Find the IP address of the server in the local network using the server port
    :param server_port: The port of the server
    :return: The IP address of the server
    """
    # Get the local network IP address and subnet mask
    output = subprocess.check_output(['ipconfig'], universal_newlines=True)
    # Get the IP address and subnet mask by using regex on the output of the ipconfig command
    ip_address = re.search(r'IPv4 Address\. . . . . . . . . . . : ([\d\.]+)', output).group(1)
    subnet_mask = re.search(r'Subnet Mask . . . . . . . . . . . : ([\d\.]+)', output).group(1)
    # Create an IPv4 network object from the IP address and subnet mask
    network_address = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)

    # Create a list to store the results of the connection attempts
    results = []

    # Create a list of threads to perform the connection attempts
    threads = []
    for device_ip in network_address.hosts():
        t = threading.Thread(target=connect_to_server, args=(str(device_ip), server_port, results))
        threads.append(t)
        t.start()

    # Add a thread to connect to the current device's IP address
    t = threading.Thread(target=connect_to_server, args=(ip_address, server_port, results))
    threads.append(t)
    t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Check the results for a successful connection
    for result in results:
        if result is not None:
            return result

    # No server was found, so return None
    return None


def connect_to_server(ip_address: str, port: int, results: list):
    """
    Attempt to connect to the server at the specified IP address and port
    :param ip_address: The IP address to connect to
    :param port: The port to connect to
    :param results: The list to append the results to
    :return: None
    """
    try:
        # Create a socket and attempt to connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip_address, port))
            # Connection succeeded, so append the device IP address to the results list
            results.append(ip_address)

    except (socket.timeout, ConnectionRefusedError):
        # Connection failed or timed out, so append None to the results list
        results.append(None)


def main():
    server_ip = detect_server_locally(3108)
    if server_ip is None:
        print("Strife server not detected in the local network. using the default IP address in the config file.")
        server_ip = config.server_ip

    # Create the communication objects, the queues and start the threads
    general_queue = queue.Queue()
    general_com = ClientCom(3108, server_ip, general_queue)
    threading.Thread(target=handle_general_messages, args=(general_com, general_queue,), daemon=True).start()

    chats_queue = queue.Queue()
    chats_com = ClientCom(2907, server_ip, chats_queue, com_type='chats')
    threading.Thread(target=handle_chats_messages, args=(chats_com, chats_queue,), daemon=True).start()

    files_queue = queue.Queue()
    files_com = ClientCom(3103, server_ip, files_queue, com_type='files')
    threading.Thread(target=handle_files_messages, args=(files_com, files_queue,), daemon=True).start()

    # Wait for the connection to the server
    while not general_com.running:
        pass

    # Change the working directory to the root of the project
    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))
    # Initialize the keys manager and the file handler
    FileHandler.initialize(str(wd) + '\\files')

    # Start the GUI
    app = wx.App()
    main_frame = MainFrame(parent=None, title='Strife', general_com=general_com,
                           chats_com=chats_com, files_com=files_com)
    main_frame.Show()
    app.MainLoop()

    # When the GUI is closed, close the threads
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    main()
