class Protocol:
    """
    A class for creating and deconstructing messages (client side) according to the protocol
    """

    def __init__(self):
        # A char for separating fields in the message
        self.FIELD_SEPARATOR = '@'
        # A chat for separating items in a list of items in a field
        self.LIST_SEPARATOR = '$'

        # Opcodes to construct messages (client -> server)
        self.general_opcodes = {
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
        self.chat_opcodes = {
            'text_message': 1,
            'file_description': 2
        }
        self.files_opcodes = {
            'file_in_chat': 1,
            'profile_pic_change': 2
        }

        # Opcodes to read messages (server -> client)
        self.s_general_opcodes = {
            1: 'approve_reject',
            2: 'friend_request',
            3: 'added_to_group',
            5: 'voice_call_started',
            6: 'video_call_started',
            7: 'voice_call_info',
            8: 'video_call_info',
            9: 'voice_user_joined',
            10: 'video_user_joined',
            11: 'chats_list',
            12: 'group_members',
            13: 'user_status',
            14: 'friend_added'
        }
        self.s_chat_opcodes = {
            1: 'text_message',
            2: 'file_description'
        }
        self.s_files_opcodes = {
            1: 'file_in_chat',
            2: 'user_profile_picture'
        }

        # Parameters of every message from the server
        self.s_opcodes_params = {
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
            'text_message': ('message',),
            'file_description': ('file_name', 'file_size', 'file_hash'),
            'file_in_chat': ('chat_id', 'file_name', 'file_hash', 'file_contents'),
            'user_profile_picture': ('pfp_username', 'image_contents')
        }

    def register(self, username, password):
        # Get the opcode of register
        opcode = self.general_opcodes['register']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}{self.FIELD_SEPARATOR}{password}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def sign_in(self, username, password):
        # Get the opcode of sign_in
        opcode = self.general_opcodes['sign_in']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}{self.FIELD_SEPARATOR}{password}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def add_friend(self, username):
        # Get the opcode of add_friend
        opcode = self.general_opcodes['add_friend']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def create_group(self, group_name, group_members):
        # Get the opcode of create_group
        opcode = self.general_opcodes['create_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{group_name}{self.FIELD_SEPARATOR}"
        # Add all the members as a list to the message
        for member in group_members:
            msg += self.LIST_SEPARATOR + member
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def start_voice(self, group_id):
        # Get the opcode of start_voice
        opcode = self.general_opcodes['start_voice']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{group_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def start_video(self, group_id):
        # Get the opcode of start_video
        opcode = self.general_opcodes['start_video']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{group_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def change_username(self, new_username):
        # Get the opcode of change_username
        opcode = self.general_opcodes['change_username']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{new_username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def change_pfp(self, picture):
        # Get the opcode of change_pfp
        kind = self.files_opcodes['profile_pic_change']
        # Construct the message
        msg = f"{kind}{self.FIELD_SEPARATOR}{len(picture)}{self.FIELD_SEPARATOR}{picture}"
        # The the message size
        size = len(msg) - len(picture)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def change_status(self, new_status):
        # Get the opcode of change_status
        opcode = self.general_opcodes['change_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{new_status}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def change_password(self, old_password, new_password):
        # Get the opcode of change_password
        opcode = self.general_opcodes['change_password']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{old_password}{self.FIELD_SEPARATOR}{new_password}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def get_chat_history(self, chat_id):
        # Get the opcode of get_chat_history
        opcode = self.general_opcodes['get_chat_history']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def request_file(self, chat_id, file_hash):
        # Get the opcode of request_file
        opcode = self.general_opcodes['request_file']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}{file_hash}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def remove_friend(self, username):
        # Get the opcode of remove_friend
        opcode = self.general_opcodes['remove_friend']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def join_voice(self, chat_id):
        # Get the opcode of join_voice
        opcode = self.general_opcodes['join_voice']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def join_video(self, chat_id):
        # Get the opcode of join_video
        opcode = self.general_opcodes['join_video']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def add_member_to_group(self, chat_id, username):
        # Get the opcode of add_member_to_group
        opcode = self.general_opcodes['add_member_to_group']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}{self.FIELD_SEPARATOR}{username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def request_group_members(self, chat_id):
        # Get the opcode of request_group_members
        opcode = self.general_opcodes['request_group_members']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{chat_id}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def request_user_pfp(self, username):
        # Get the opcode of request_user_pfp
        opcode = self.general_opcodes['request_user_pfp']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def request_user_status(self, username):
        # Get the opcode of request_user_status
        opcode = self.general_opcodes['request_user_status']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}{self.FIELD_SEPARATOR}{username}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def request_chats(self):
        # Get the opcode of request_chats
        opcode = self.general_opcodes['request_chats']
        # Construct the message
        msg = f"{str(opcode).zfill(2)}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def send_message(self, sender_username, chat_id, message):
        # Get the opcode of send_message
        kind = self.chat_opcodes['send_message']
        # Construct the message
        msg = f"{kind}{str(chat_id).zfill(3)}{self.FIELD_SEPARATOR}{sender_username}{self.FIELD_SEPARATOR}{message}"
        # The the message size
        size = len(msg)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def send_image(self, chat_id, image_name, image):
        # TODO: Check if hash is really needed to be send
        # Get the opcode of send_image
        kind = self.files_opcodes['file_in_chat']
        # Construct the message
        msg = f"{kind}{self.FIELD_SEPARATOR}{len(image)}{self.FIELD_SEPARATOR}{chat_id}" \
            f"{self.FIELD_SEPARATOR}{image_name}{self.FIELD_SEPARATOR}{image} "
        # The the message size
        size = len(msg) - len(image)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def send_file(self, chat_id, file_name, file):
        # TODO: Check if hash is really needed to be send
        # Get the opcode of send_file
        kind = self.files_opcodes['file_in_chat']
        # Construct the message
        msg = f"{kind}{self.FIELD_SEPARATOR}{len(file)}{self.FIELD_SEPARATOR}{chat_id}" \
            f"{self.FIELD_SEPARATOR}{file_name}{self.FIELD_SEPARATOR}{file} "
        # The the message size
        size = len(msg) - len(file)
        # Return the message after protocol
        return f'{str(size).zfill(2)}{msg}'

    def unprotocol_msg(self, type, raw_message):
        """
        Deconstructs a message received from the server with the client-server's protocol
        :param type: The type of the message (general, chat, file)
        :param raw_message: The message
        :return: A dict with every parameter name as the key and it's value as the value
        """
        # Split the message into it's fields with the field separator
        values = raw_message.split(self.FIELD_SEPARATOR)

        # Get the opcode of the message
        opcode = int(values[0])
        values = values[1:]

        # The returned dict
        ret = {}

        # If the message was received in the general messages channel
        if type == 'general':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.s_general_opcodes[opcode]
            ret['opname'] = opcode_name

            # Get the parameters names of the message
            params_names = self.s_opcodes_params[self.s_general_opcodes[opcode]]

            # Assign a value for each parameter in a dict
            for i in range(len(values)):
                value = values[i]
                param_name = params_names[i]

                # If the value is a list
                if len(value.split(self.LIST_SEPARATOR)) > 1:
                    # Check if the list is of integers
                    if value.split(self.LIST_SEPARATOR)[0].isnumberic():
                        ret[param_name] = [int(v) for v in value.split(self.LIST_SEPARATOR)]
                    else:
                        ret[param_name] = value.split(self.LIST_SEPARATOR)

                # If the value isn't a list
                else:
                    # Check if the value is an integer
                    if value.isnumeric():
                        ret[param_name] = int(value)
                    else:
                        ret[param_name] = value

        # If the message was received in the chat messages channel
        elif type == 'chat':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.s_chat_opcodes[opcode]
            ret['opname'] = opcode_name

            # Get the parameters names of the message
            params_names = self.s_opcodes_params[self.s_chat_opcodes[opcode]]

            # Assign a value for each parameter in a dict
            for i in range(len(values)):
                value = values[i]
                param_name = params_names[i]

                # If the value is a list
                if len(value.split(self.LIST_SEPARATOR)) > 1:
                    # Check if the list is of integers
                    if value.split(self.LIST_SEPARATOR)[0].isnumberic():
                        ret[param_name] = [int(v) for v in value.split(self.LIST_SEPARATOR)]
                    else:
                        ret[param_name] = value.split(self.LIST_SEPARATOR)

                # If the value isn't a list
                else:
                    # Check if the value is an integer
                    if value.isnumeric():
                        ret[param_name] = int(value)
                    else:
                        ret[param_name] = value

        # If the message was received in the files messages channel
        elif type == 'files':
            # The first value in the dict is the opcode's name (opname)
            opcode_name = self.s_files_opcodes[opcode]
            ret['opname'] = opcode_name

            # Get the parameters names of the message
            params_names = self.s_opcodes_params[self.s_files_opcodes[opcode]]

            # Assign a value for each parameter in a dict
            for i in range(len(values)):
                value = values[i]
                param_name = params_names[i]

                # If the value is a list
                if len(value.split(self.LIST_SEPARATOR)) > 1:
                    # Check if the list is of integers
                    if value.split(self.LIST_SEPARATOR)[0].isnumberic():
                        ret[param_name] = [int(v) for v in value.split(self.LIST_SEPARATOR)]
                    else:
                        ret[param_name] = value.split(self.LIST_SEPARATOR)

                # If the value isn't a list
                else:
                    # Check if the value is an integer
                    if value.isnumeric():
                        ret[param_name] = int(value)
                    else:
                        ret[param_name] = value

        return ret

