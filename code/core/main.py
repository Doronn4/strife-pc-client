import os
import time
from pathlib import Path

from code.core.client_com import ClientCom
from code.core.client_protocol import Protocol
import threading
import queue
from code.core.keys_manager import KeysManager


general_dict = {
}


def handle_general_message(com, queue):
    """
    Handle general messages incoming from the server
    """
    while True:
        # Take the data from the queue
        data = queue.get()
        # Un-protocol the message from the server
        msg = Protocol.unprotocol_msg("general", data)
        print(msg)
        # Check if the name of the operation is in the dict of functions
        if msg['opname'] in general_dict.keys():
            # Call the function according to the operation
            general_dict[msg['opname']](com, msg)


if __name__ == '__main__':
    general_queue = queue.Queue()
    general_com = ClientCom(1000, '127.0.0.1', general_queue)

    messages_queue = queue.Queue()
    message_com = ClientCom(2000, '127.0.0.1', messages_queue)

    threading.Thread(target=handle_general_message, args=(general_com, general_queue,)).start()

    # Wait for the connection to the server
    while not general_com.running:
        pass

    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    KeysManager.initialize(str(wd)+'keys.json')

    msg = Protocol.register("ariel4", "12345")
    general_com.send_data(msg)

    msg = Protocol.sign_in("ariel4", "12345")
    general_com.send_data(msg)

    msg = Protocol.create_group("my new group!")
    general_com.send_data(msg)

    time.sleep(3)

    msg = Protocol.send_message('ariel4', 1, 'a message on my group')
    message_com.send_data(msg)

