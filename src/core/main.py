import os
import time
from pathlib import Path
from src.core.client_com import ClientCom
from src.core.client_protocol import Protocol
import threading
import queue
from src.core.keys_manager import KeysManager
import config


general_dict = {
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
        # Check if the name of the operation is in the dict of functions
        if message['opname'] in general_dict.keys():
            # Call the function according to the operation
            general_dict[message['opname']](com, message)


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

    # Temp for testing  ----------------------

    msg = Protocol.register("ariel4", "12345")
    general_com.send_data(msg)

    msg = Protocol.sign_in("ariel4", "12345")
    general_com.send_data(msg)

    msg = Protocol.create_group("my new group!")
    general_com.send_data(msg)

    time.sleep(3)

    msg = Protocol.send_message('ariel4', 1, 'a message on my group')
    print('sent msg')
    chats_com.send_data(msg)

    # Temp for testing  ----------------------


if __name__ == '__main__':
    main()
