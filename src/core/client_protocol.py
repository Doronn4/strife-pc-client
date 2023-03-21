class Protocol:
    """
    A class for creating and deconstructing messages (client side) according to the protocol
    """

    # A char for separating fields in the message
    FIELD_SEPARATOR = '@'
    # A chat for separating items in a list of items in a field
    LIST_SEPARATOR = '#'

    # Opcodes to construct messages (client -> server)
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
        'request_chats': 19,
        'accept_friend': 20
    }
    chat_opcodes = {
        'text_message': 1,
        'file_description': 2
    }
    files_opcodes = {
        'file_in_chat': 1,
        'profile_pic_change': 2
    }

    # Opcodes to read messages (server -> client)
    s_general_opcodes = {
        1: 'approve_reject',
        2: 'friend_request',
        3: 'added_to_group',
        4: 'voice_call_started',
        5: 'video_call_started',
        6: 'voice_call_info',
        7: 'video_call_info',
        8: 'voice_user_joined',
        9: 'video_user_joined',
        10: 'chats_list',
        11: 'group_members',
        12: 'user_status',
        13: 'friend_added'
    }
    s_chat_opcodes = {
        1: 'text_message',
        2: 'file_description',
        3: 'chat_history'
    }
    s_files_opcodes = {
        1: 'file_in_chat',
        2: 'user_profile_picture'
    }

    # Parameters of every message from the server (server -> client)
    s_opcodes_params = {
        'approve_reject': ('is_approved', 'function_opcode'),
        'friend_request': ('sender_username',),
        'added_to_group': ('group_name', 'chat_id', 'group_key'),
        'voice_call_started': ('chat_id',),
        'video_call_started': ('chat_id',),
        'voice_call_info': ('chat_id', 'ips', 'usernames'),
        'video_call_info': ('chat_id', 'ips', 'usernames'),
        'voice_call_user_joined': ('chat_id', 'user_ip', 'username'),
        'video_call_user_joined': ('chat_id', 'user_ip', 'username'),
        'chats_list': ('chats_names', 'chats_ids'),
        'group_members': ('chat_ids', 'usernames'),
        'user_status': ('username', 'status'),
        'friend_added': ('friend_username',),
        'text_message': ('chat_id', 'sender', 'message'),
        'file_description': ('file_name', 'file_size', 'file_hash'),
        'file_in_chat': ('chat_id', 'file_name', 'file_hash', 'file_contents'),
        'user_profile_picture': ('pfp_username', 'image_contents'),
        'chat_history': ('messages',)
    }

    @staticmethod
    def register(username, password):
        # Get the opcode of register
        opcode = Protocol.general_opcodes['register']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}{Protocol.FIELD_SEPARATOR}{password}"
        return msg

    @staticmethod
    def sign_in(username, password):
        # Get the opcode of sign_in
        opcode = Protocol.general_opcodes['sign_in']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}{Protocol.FIELD_SEPARATOR}{password}"
        # Return the message after protocol
        return msg

    @staticmethod
    def add_friend(username):
        # Get the opcode of add_friend
        opcode = Protocol.general_opcodes['add_friend']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def accept_friend_request(friend_username, is_accepted: bool):
        # Get the opcode of accept friend
        opcode = Protocol.general_opcodes['accept_friend']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{friend_username}{Protocol.FIELD_SEPARATOR}{is_accepted}"
        # Return the message after protocol
        return msg

    @staticmethod
    def create_group(group_name):
        # Get the opcode of create_group
        opcode = Protocol.general_opcodes['create_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{group_name}"
        # Return the message after protocol
        return msg

    @staticmethod
    def start_voice(group_id):
        # Get the opcode of start_voice
        opcode = Protocol.general_opcodes['start_voice']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{group_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def start_video(group_id):
        # Get the opcode of start_video
        opcode = Protocol.general_opcodes['start_video']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{group_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def change_username(new_username):
        # Get the opcode of change_username
        opcode = Protocol.general_opcodes['change_username']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{new_username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def change_pfp(picture):
        # Get the opcode of change_pfp
        kind = Protocol.files_opcodes['profile_pic_change']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{len(picture)}{Protocol.FIELD_SEPARATOR}{picture}"
        # Return the message after protocol
        return msg

    @staticmethod
    def change_status(new_status):
        # Get the opcode of change_status
        opcode = Protocol.general_opcodes['change_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{new_status}"
        # Return the message after protocol
        return msg

    @staticmethod
    def change_password(old_password, new_password):
        # Get the opcode of change_password
        opcode = Protocol.general_opcodes['change_password']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{old_password}{Protocol.FIELD_SEPARATOR}{new_password}"
        # Return the message after protocol
        return msg

    @staticmethod
    def get_chat_history(chat_id):
        # Get the opcode of get_chat_history
        opcode = Protocol.general_opcodes['get_chat_history']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def request_file(chat_id, file_hash):
        # Get the opcode of request_file
        opcode = Protocol.general_opcodes['request_file']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}{file_hash}"
        # Return the message after protocol
        return msg

    @staticmethod
    def remove_friend(username):
        # Get the opcode of remove_friend
        opcode = Protocol.general_opcodes['remove_friend']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def join_voice(chat_id):
        # Get the opcode of join_voice
        opcode = Protocol.general_opcodes['join_voice']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def join_video(chat_id):
        # Get the opcode of join_video
        opcode = Protocol.general_opcodes['join_video']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def add_member_to_group(chat_id, username, group_key):
        # Get the opcode of add_member_to_group
        opcode = Protocol.general_opcodes['add_member_to_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}{Protocol.FIELD_SEPARATOR}{username}{Protocol.FIELD_SEPARATOR}{group_key} "
        # Return the message after protocol
        return msg

    @staticmethod
    def request_group_members(chat_id):
        # Get the opcode of request_group_members
        opcode = Protocol.general_opcodes['request_group_members']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{chat_id}"
        # Return the message after protocol
        return msg

    @staticmethod
    def request_user_pfp(username):
        # Get the opcode of request_user_pfp
        opcode = Protocol.general_opcodes['request_user_picture']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def request_user_status(username):
        # Get the opcode of request_user_status
        opcode = Protocol.general_opcodes['request_user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{Protocol.FIELD_SEPARATOR}{username}"
        # Return the message after protocol
        return msg

    @staticmethod
    def request_chats():
        # Get the opcode of request_chats
        opcode = Protocol.general_opcodes['request_chats']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}"
        # Return the message after protocol
        return msg

    @staticmethod
    def send_message(sender_username, chat_id, message):
        # Get the opcode of send_message
        kind = Protocol.chat_opcodes['text_message']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{str(chat_id).zfill(3)}{Protocol.FIELD_SEPARATOR}{sender_username}{Protocol.FIELD_SEPARATOR}{message} "
        # Return the message after protocol
        return msg

    @staticmethod
    def send_image(chat_id, image_name, image):
        # TODO: Check if hash is really needed to be send
        # Get the opcode of send_image
        kind = Protocol.files_opcodes['file_in_chat']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{len(image)}{Protocol.FIELD_SEPARATOR}{chat_id}" \
            f"{Protocol.FIELD_SEPARATOR}{image_name}{Protocol.FIELD_SEPARATOR}{image} "
        # Return the message after protocol
        return msg

    @staticmethod
    def send_file(chat_id, file_name, file):
        # TODO: Check if hash is really needed to be send
        # Get the opcode of send_file
        kind = Protocol.files_opcodes['file_in_chat']
        # Construct the message
        msg = f"{kind}{Protocol.FIELD_SEPARATOR}{len(file)}{Protocol.FIELD_SEPARATOR}{chat_id}" \
            f"{Protocol.FIELD_SEPARATOR}{file_name}{Protocol.FIELD_SEPARATOR}{file} "
        # Return the message after protocol
        return msg

    @staticmethod
    def unprotocol_msg(type: str, raw_message):
        """
        Deconstructs a message received from the server with the client-server's protocol
        :param type: The type of the message (general, chat, file)
        :param raw_message: The message
        :return: A dict with every parameter name as the key and it's value as the value
        """
        # Split the message into it's fields with the field separator
        values = raw_message.split(Protocol.FIELD_SEPARATOR)

        # Get the opcode of the message
        opcode = int(values[0])
        values = values[1:]

        # The returned dict
        ret = {}

        params_names = []

        # If the message was received in the general messages channel
        if type == 'general':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = Protocol.s_general_opcodes[opcode]
            ret['opname'] = opcode_name
            # Get the parameters names of the message
            params_names = Protocol.s_opcodes_params[Protocol.s_general_opcodes[opcode]]

        # If the message was received in the chat messages channel
        elif type == 'chat':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = Protocol.s_chat_opcodes[opcode]
            ret['opname'] = opcode_name
            # Get the parameters names of the message
            params_names = Protocol.s_opcodes_params[Protocol.s_chat_opcodes[opcode]]

        # If the message was received in the files messages channel
        elif type == 'files':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = Protocol.s_files_opcodes[opcode]
            ret['opname'] = opcode_name
            # Get the parameters names of the message
            params_names = Protocol.s_opcodes_params[Protocol.s_files_opcodes[opcode]]

        # Assign a value for each parameter in a dict
        for i in range(len(values)):
            value = values[i]
            param_name = params_names[i]

            # If the value is a list
            if len(value.split(Protocol.LIST_SEPARATOR)) > 1:
                # Check if the list is of integers
                if value.split(Protocol.LIST_SEPARATOR)[0].isnumeric():
                    ret[param_name] = [int(v) for v in value.split(Protocol.LIST_SEPARATOR)]
                else:
                    ret[param_name] = value.split(Protocol.LIST_SEPARATOR)

            # If the value isn't a list
            else:
                # Check if the value is an integer
                if value.isnumeric():
                    ret[param_name] = int(value)
                else:
                    ret[param_name] = value
        return ret


if __name__ == '__main__':
    message = Protocol.register('doron', '12323k')
    print(message)

