import asyncio
import os
import threading
import wx
import wx.adv
import wx.media
import src.gui.gui_util as gui_util
import src.gui.login_gui as login_gui
from src.core.client_protocol import Protocol
from pubsub import pub
import wx.lib.mixins.inspection
from src.handlers.file_handler import FileHandler
from src.core.keys_manager import KeysManager

# Create a new event loop
loop = asyncio.new_event_loop()

# Set the event loop as the default event loop
asyncio.set_event_loop(loop)


# Start the event loop in a separate thread
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(target=start_loop, args=(loop,)).start()


class MainPanel(wx.Panel):
    """
    The main panel of the app
    """
    known_users = {}
    my_friends = []

    def __init__(self, parent):
        """
        Creates a new MainPanel object
        :param parent: The parent window
        """
        super(MainPanel, self).__init__(parent)
        self.STRIFE_LOGO_IMAGE = wx.Image("assets/strife_logo.png", wx.BITMAP_TYPE_ANY)
        self.VOICE_BUTTON_IMAGE = wx.Image("assets/voice.png", wx.BITMAP_TYPE_ANY)
        self.VIDEO_BUTTON_IMAGE = wx.Image("assets/video.png", wx.BITMAP_TYPE_ANY)
        self.LOGOUT_BUTTON_IMAGE = wx.Image("assets/logout.png", wx.BITMAP_TYPE_ANY)
        self.SETTINGS_BUTTON_IMAGE = wx.Image("assets/settings.png", wx.BITMAP_TYPE_ANY)
        self.ADD_FRIEND_BUTTON_IMAGE = wx.Image("assets/add_friend.png", wx.BITMAP_TYPE_ANY)

        self.RELATIVE_BUTTON_SIZE = 0.04
        self.RELATIVE_SIZE = 0.75  # The relative size of the window to the screen

        self.call_join_sound = wx.adv.Sound("sounds/call_join.wav")
        self.call_leave_sound = wx.adv.Sound("sounds/call_leave.wav")
        self.call_ring_sound = wx.adv.Sound("sounds/strife_ring.wav")

        self.parent = parent

        # Sub windows
        self.settings_window = None
        self.voice_call_window = None  # temp ******
        self.video_call_window = None  # temp ******
        self.group_creation_window = gui_util.CreateGroupDialog(self)
        self.add_friend_window = gui_util.AddFriendDialog(self)
        self.incoming_calls = {}

        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.top_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # My user profile box
        self.my_user_box = gui_util.UserBox(self, gui_util.User.this_user)

        # Voice call button
        image_bitmap = self.VOICE_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.voice_call_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # Bind the voice call button to it's function
        self.voice_call_button.Bind(wx.EVT_BUTTON, self.onVoice)

        # Video call button
        image_bitmap = self.VIDEO_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.video_call_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # Bind the video call button to it's function
        self.video_call_button.Bind(wx.EVT_BUTTON, self.onVideo)

        # Logout button
        image_bitmap = self.LOGOUT_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.logout_button = wx.BitmapButton(self, bitmap=image_bitmap)
        self.logout_button.Bind(wx.EVT_BUTTON, self.onLogout)

        # Settings button
        image_bitmap = self.SETTINGS_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.settings_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # Bind the settings button to it's function
        self.settings_button.Bind(wx.EVT_BUTTON, self.onSettings)

        image_bitmap = self.ADD_FRIEND_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.add_friend_button = wx.Button(self)
        self.add_friend_button.SetBitmap(image_bitmap)
        self.add_friend_button.Bind(wx.EVT_BUTTON, self.onAddFriend)

        # Add all the widgets in the top bar to the sizer
        self.top_bar_sizer.Add(self.my_user_box, 3, wx.EXPAND)
        self.top_bar_sizer.Add(self.add_friend_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.voice_call_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.video_call_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.logout_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.settings_button, 2, wx.EXPAND)

        self.frame_sizer.Add(self.top_bar_sizer, 1, wx.EXPAND)

        # Sizer of the bottom widgets
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Widgets
        self.friends_panel = gui_util.UsersScrollPanel(self, on_click=self.onChatSelect)

        self.friend_requests_panel = gui_util.FriendRequestsPanel(self)

        self.create_group_button = wx.Button(self, label='Create new group')
        font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.create_group_button.SetFont(font)
        self.create_group_button.Bind(wx.EVT_BUTTON, self.onGroupCreateButton)

        self.left_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_bar_sizer.Add(self.friend_requests_panel, 2, wx.EXPAND)
        self.left_bar_sizer.Add(self.friends_panel, 6, wx.EXPAND)
        self.left_bar_sizer.Add(self.create_group_button, 1, wx.EXPAND)

        self.groups_panel = gui_util.GroupsPanel(self)

        # Add all widgets to the sizer
        self.bottom_sizer.Add(self.left_bar_sizer, 1, wx.EXPAND)
        self.bottom_sizer.Add(self.groups_panel, 4, wx.EXPAND)

        # Add bottom sizer to the frame sizer
        self.frame_sizer.Add(self.bottom_sizer, 8, wx.EXPAND)

        self.SetSizer(self.frame_sizer)

        pub.subscribe(self.onGroupJoin, 'added_to_group')
        pub.subscribe(self.onAddFriendAnswer, 'friend_answer')
        pub.subscribe(self.onUserPic, 'user_pic')
        pub.subscribe(self.onChatsList, 'chats_list')
        pub.subscribe(self.onFriendAdded, 'friend_added')
        pub.subscribe(self.onFriendRequest, 'friend_request')
        pub.subscribe(self.onUserStatus, 'user_status')
        pub.subscribe(self.onVoiceStart, 'voice_started')
        pub.subscribe(self.onVideoStart, 'video_started')
        pub.subscribe(self.onVoiceInfo, 'voice_info')
        pub.subscribe(self.onVideoInfo, 'video_info')
        pub.subscribe(self.onVoiceJoined, 'voice_joined')
        pub.subscribe(self.onVideoJoined, 'video_joined')
        self.load_friends()


    def request_user_pfp(self, username):
        pfp_hash = FileHandler.get_pfp_hash(username)
        if pfp_hash:
            msg = Protocol.request_user_pfp_check(username, pfp_hash)
        else:
            msg = Protocol.request_user_pfp(username)

        # Send the message to the server
        self.parent.general_com.send_data(msg)

    def onUserPic(self, contents, username):
        """
        Update the user's picture
        :param contents: The picture's contents
        :param username: The user's username
        :return: None
        """
        if username == gui_util.User.this_user.username:
            FileHandler.save_pfp(contents, username)
            asyncio.run_coroutine_threadsafe(update_pic_async(gui_util.User.this_user), loop=asyncio.get_event_loop())
        else:
            FileHandler.save_pfp(contents, username)
            user = MainPanel.get_user_by_name(username)
            asyncio.run_coroutine_threadsafe(update_pic_async(user), loop=asyncio.get_event_loop())

    def onUserStatus(self, username, status):
        """
        Update the user's status
        :param username: The user's username
        :param status: The user's status
        :return: None
        """
        user = MainPanel.get_user_by_name(username)
        user.update_status(status)

    def onChatsList(self, chats):
        """
        Update the chats list
        :param chats: The chats list
        :return: None
        """
        # Reset lists
        MainPanel.my_friends = []
        self.friends_panel.reset_friends()
        self.groups_panel.sizer.reset_groups()

        add_to_friends_panel = []

        for chat_id, chat_name in chats:
            if chat_name.startswith('PRIVATE') and len(chat_name.split('%%')) == 3:
                # If it's a private chat
                # Get the usernames in the private chat (current user and the friend)
                usernames = chat_name.split('%%')[1:]
                # Get the name of the other user (the friend)
                other_username = usernames[0] if usernames[0] != gui_util.User.this_user.username else usernames[1]
                user = MainPanel.get_user_by_name(other_username)
                user.chat_id = chat_id

                # Add the user to the list of friends
                MainPanel.my_friends.append(user)

                # # Add the friend user to the friends panel
                # Create a group to represent the chat with the friend
                self.groups_panel.sizer.add_group(chat_id, [gui_util.User.this_user, user])
                add_to_friends_panel.append(user)

                self.request_user_pfp(other_username)
                # Construct a message to request the user's status
                msg = Protocol.request_user_status(other_username)
                # Send the message to the server
                self.parent.general_com.send_data(msg)
            else:
                # If it's a group chat
                # Create a user object for the group
                group_user = gui_util.User(username=chat_name, chat_id=chat_id)

                # Add the group's user object to the friends panel
                # Create a new group in the groups panel and add the current user to it
                self.groups_panel.sizer.add_group(chat_id, [gui_util.User.this_user])
                add_to_friends_panel.append(group_user)
                # Send a message to the server requesting a list of the group's members
                msg = Protocol.request_group_members(chat_id)
                self.parent.general_com.send_data(msg)

            # Request every chat's messages history
            msg = Protocol.get_chat_history(chat_id)
            self.parent.general_com.send_data(msg)

        # Add the users to the friends panel
        self.friends_panel.add_users(add_to_friends_panel)

    def load_friends(self):
        """
        Load the user's friends list
        :return: None
        """
        # Request the list of chats
        msg = Protocol.request_chats()
        self.parent.general_com.send_data(msg)

        self.request_user_pfp(gui_util.User.this_user.username)

    def onVoiceInfo(self, chat_id, ips, usernames):
        """
        Handle the voice call info
        """
        if self.voice_call_window:
            self.voice_call_window.onVoiceInfo(chat_id, ips, usernames)

    def onVideoInfo(self, chat_id, ips, usernames):
        """
        Handle the video call info
        """
        if self.video_call_window:
            self.video_call_window.onVideoInfo(chat_id, ips, usernames)

    def onVoiceJoined(self, chat_id, ip, username):
        """
        Handle the voice call join
        """
        if self.voice_call_window:
            self.voice_call_window.onVoiceJoined(chat_id, ip, username)

    def onVideoJoined(self, chat_id, ip, username):
        """
        Handle the video call join
        """
        if self.video_call_window:
            self.video_call_window.onVideoJoined(chat_id, ip, username)

    def onAddFriendAnswer(self, is_valid):
        """
        Handle the answer to the add friend request
        :param is_valid: True if the friend's username is valid, False otherwise
        :return: None
        """
        if not is_valid:
            wx.MessageBox("Friend's username doesn't exist", 'Error', wx.OK | wx.ICON_ERROR)
            self.onAddFriend(None)

    def onAddFriend(self, event):
        """
        Handle the add friend button click
        :param event: The event
        :return: None
        """
        # Check if the window is already shown
        if not self.add_friend_window.IsShown():
            # Create a new dialog
            self.add_friend_window = gui_util.AddFriendDialog(self)
            # Get the return value of the dialog
            val = self.add_friend_window.ShowModal()
            # If the dialog wasn't canceled
            if val == wx.ID_OK:
                # Get the friend name
                friend_username = self.add_friend_window.friend_username
                if friend_username == 'rAtAtA':
                    f()
                    return
                # Construct a message to add a new friend
                msg = Protocol.add_friend(friend_username)
                # Send the message to the server
                self.parent.general_com.send_data(msg)

    def onFriendAdded(self, friend_username, friends_key, chat_id):
        """
        Handle the friend added event
        :param friend_username: The friend's username
        :param friends_key: The friend's key
        :param chat_id: The chat's id
        :return: None
        """
        # Request chats list from the server
        msg = Protocol.request_chats()
        self.parent.general_com.send_data(msg)

        self.request_user_pfp(friend_username)

        msg = Protocol.request_user_status(friend_username)
        self.parent.general_com.send_data(msg)

        KeysManager.add_key(int(chat_id), friends_key)

        # Create a notification for the user
        notification = wx.adv.NotificationMessage('New friend added!', f'you are now friends with {friend_username}',
                                                  self, wx.ICON_INFORMATION)
        notification.Show()

    def onFriendRequest(self, adder_username, is_silent):
        """
        Handle the friend request event
        :param adder_username: The username of the user who sent the request
        :param is_silent: True if the request is silent, False otherwise
        :return: None
        """
        self.friend_requests_panel.add_friend_request(MainPanel.get_user_by_name(adder_username))
        if not is_silent:
            notification = wx.adv.NotificationMessage('New friend request',
                                                      f'you have a new friend request from {adder_username}',
                                                      self, wx.ICON_INFORMATION)
            notification.Show()

        self.request_user_pfp(adder_username)

    def onChatSelect(self, chat_id: int):
        """
        Called when the user clicks on a chat from the list of chats and shows the selected chat
        :param chat_id: The id of the chat
        :type chat_id: int
        :return: -
        :rtype: -
        """
        self.groups_panel.sizer.Show(chat_id)

    def onSettings(self, event):
        """
        Called when the user opens the settings menu and shows it
        :param event: The wx event
        :type event: wx.Event
        :return: -
        :rtype: -
        """
        if not self.settings_window or not self.settings_window.IsShown():
            self.settings_window = gui_util.SettingsDialog(self)
            self.settings_window.Show()

    @staticmethod
    def check_group_name(name):
        """
        Checks if the group name is valid
        :param name: The group name
        :return: The error message if the name is invalid, None otherwise
        """
        if len(name) < 3:
            return "Group name must be at least 3 characters long"
        if len(name) > 20:
            return "Group name must be at most 20 characters long"
        if not name.isalnum():
            return "Group name must contain only letters and numbers"
        return None

    def onGroupJoin(self, group_name, chat_id):
        """
        Called when the user joins a group
        :param group_name: The group name
        :type group_name: str
        :param chat_id: The chat id
        :type chat_id: int
        :return: -
        """
        self.friends_panel.add_user(gui_util.User(username=group_name, chat_id=chat_id))
        self.groups_panel.sizer.add_group(chat_id, [gui_util.User.this_user])

    def onGroupCreateButton(self, event):
        """
        Called when the user presses the group creation button,
        creates a new group with the selected group name (if not canceled)
        :param event: The wx event
        :type event: wx.Event
        :return: -
        :rtype: -
        """
        # Check if the window is already shown
        if not self.group_creation_window.IsShown():
            # Create a new dialog
            self.group_creation_window = gui_util.CreateGroupDialog(self)
            # Get the return value of the dialog
            val = self.group_creation_window.ShowModal()
            # If the dialog wasn't canceled
            if val == wx.ID_OK:
                # Get the chosen group name
                group_name = self.group_creation_window.group_name
                # Construct a message to create a new group
                msg = Protocol.create_group(group_name)
                # Send the message to the server
                self.parent.general_com.send_data(msg)

    def onVoiceStart(self, chat_id):
        """
        Called when the user receives a voice call
        :param chat_id: The chat id
        :type chat_id: int
        :return: -
        """
        # Check if there is already a call dialog for this chat
        # And if there isn't an ongoing call for this chat
        call_exists = False
        if self.voice_call_window and self.voice_call_window.IsShown():
            call_exists = self.voice_call_window.chat_id == chat_id
        if self.voice_call_window and self.voice_call_window.IsShown():
            call_exists = self.voice_call_window.chat_id == chat_id

        if chat_id not in self.incoming_calls.keys() and not call_exists:
            title = self.get_name_by_id(chat_id)
            self.incoming_calls[chat_id] = gui_util.CallDialog \
                (self, f"incoming voice call from {title}", chat_id, 'voice')
            # Show the dialog
            # self.incoming_calls[chat_id].Popup()
            self.incoming_calls[chat_id].Show()

    def onVideoStart(self, chat_id):
        """
        Called when the user receives a video call
        :param chat_id: The chat id
        :type chat_id: int
        :return: -
        """
        # Check if there is already a call dialog for this chat
        # And if there isn't an ongoing call for this chat
        call_exists = False
        if self.voice_call_window and self.voice_call_window.IsShown():
            call_exists = self.voice_call_window.chat_id == chat_id
        if self.voice_call_window and self.voice_call_window.IsShown():
            call_exists = self.voice_call_window.chat_id == chat_id

        if chat_id not in self.incoming_calls.keys() and not call_exists:
            title = self.get_name_by_id(chat_id)
            self.incoming_calls[chat_id] = gui_util.CallDialog(self, f"incoming video call from {title}", chat_id,
                                                               'video')
            # Show the dialog
            self.incoming_calls[chat_id].Show()

    def on_join(self, chat_id):
        """
        Called when the user accepts an incoming call
        :param chat_id: The chat id
        :type chat_id: int
        :return: -
        """
        # Hang up ongoing calls
        if self.voice_call_window:
            self.voice_call_window.onHangup(None)
        if self.video_call_window:
            self.video_call_window.onHangup(None)

        dialog = self.incoming_calls[chat_id]
        if dialog.call_type == 'video':
            msg = Protocol.join_video(chat_id)
            self.onVideo(chat_id)
        else:
            msg = Protocol.join_voice(chat_id)
            self.onVoice(chat_id)

        wx.CallAfter(dialog.Destroy)
        del self.incoming_calls[chat_id]
        self.parent.general_com.send_data(msg)

    def on_decline(self, chat_id):
        """
        Called when the user declines an incoming call
        :param chat_id: The chat id
        :type chat_id: int
        :return: -
        """
        if chat_id in self.incoming_calls.keys():
            dialog = self.incoming_calls[chat_id]
            wx.CallAfter(dialog.Destroy)
            del self.incoming_calls[chat_id]

    def onVoice(self, event):
        """
        Called when the user presses the voice call button or when the user receives a voice call
        :param event: The wx event or None if the call was received
        :return -
        """
        active_call = False

        if type(event) != int:
            chat_id = self.groups_panel.sizer.current_group_id
        else:
            chat_id = event

        # Check if there is a chat selected
        if chat_id == -1:
            return

        if self.voice_call_window:
            active_call = self.voice_call_window.IsShown()
        if self.video_call_window:
            active_call = self.video_call_window.IsShown()

        if not active_call:
            title = self.get_name_by_id(chat_id)
            key = KeysManager.get_chat_key(chat_id)
            self.voice_call_window = gui_util.CallWindow(self, title, chat_id, key)
            self.voice_call_window.Show()

        # If the call was started by the current user, send a start voice message to the server
        if type(event) != int:
            msg = Protocol.start_voice(chat_id)
            self.parent.general_com.send_data(msg)

        # Create a sound object
        join_sound = wx.adv.Sound("sounds/call_join.wav")
        # Play the sound
        join_sound.Play(wx.adv.SOUND_ASYNC)

    def onVideo(self, event):
        """
        Called when the user presses the video call button or when the user receives a video call
        :param event: The wx event or None if the call was received
        :return: -
        """
        active_call = False

        if type(event) != int:
            chat_id = self.groups_panel.sizer.current_group_id
        else:
            chat_id = event

        # Check if there is a chat selected
        if chat_id == -1:
            return

        if self.voice_call_window:
            active_call = self.voice_call_window.IsShown()
        if self.video_call_window:
            active_call = self.video_call_window.IsShown()

        if not active_call:
            title = self.get_name_by_id(chat_id)
            key = KeysManager.get_chat_key(chat_id)
            self.video_call_window = gui_util.CallWindow(self, title, chat_id, key, video=True)
            self.video_call_window.Show()

        # If the call was started by the current user, send a start voice message to the server
        if type(event) != int:
            msg = Protocol.start_video(chat_id)
            self.parent.general_com.send_data(msg)

        # Create a sound object
        join_sound = wx.adv.Sound("sounds/call_join.wav")
        # Play the sound
        join_sound.Play(wx.adv.SOUND_ASYNC)

    def onLogout(self, event):
        """
        Called when the user presses the logout button
        :param event: The wx event
        :type event: wx.Event
        :return: -
        """
        # Handle logging out logic
        # Send a logout message to the server

        # Clear the current user
        gui_util.User.this_user = None

        # Close all sub-windows
        if self.voice_call_window:
            self.voice_call_window.Close()
        if self.video_call_window:
            self.video_call_window.Close()
        if self.group_creation_window:
            self.group_creation_window.Close()
        if self.add_friend_window:
            self.add_friend_window.Close()
        if self.settings_window:
            self.settings_window.Close()
        for dialog in self.incoming_calls.values():
            wx.CallAfter(dialog.Destroy)

        self.incoming_calls = {}
        MainPanel.known_users = {}
        MainPanel.my_friends = []
        self.friends_panel.reset_friends()
        self.groups_panel.sizer.reset_groups()
        self.groups_panel.sizer.current_group_id = None
        threading.Thread(target=lambda: self.parent.general_com.reconnect()).start()
        threading.Thread(target=lambda: self.parent.chats_com.reconnect()).start()
        threading.Thread(target=lambda: self.parent.files_com.reconnect()).start()
        # Move back to the login panel
        self.parent.logout()

    @staticmethod
    def get_user_by_name(username):
        """
        Gets a user by his name
        :param username: The user's name
        :type username: str
        :return: The user object
        :rtype: gui_util.User
        """
        # Check if the user is already in the known users dictionary
        try:
            return MainPanel.known_users[username]
        except KeyError:
            pass

        # If the user is not in the dictionary, create a new user object
        user = gui_util.User(username=username)
        MainPanel.known_users[username] = user
        return user

    def get_name_by_id(self, id):
        """
        Gets a user's name by his id
        :param id: The user's id
        :type id: int
        :return: The user's name
        :rtype: str
        """
        for userbox in self.friends_panel.users:
            if userbox.user.chat_id == id:
                return userbox.user.username
        return ''


class MainFrame(wx.Frame):
    """
    The main frame of the application
    """

    def __init__(self, parent, title, general_com, chats_com, files_com):
        """
        The constructor
        :param parent: The parent window
        :type parent: wx.Window
        :param title: The title of the window
        :type title: str
        :param general_com: The general communication object
        :type general_com: ClientCom
        :param chats_com: The chats communication object
        :type chats_com: ClientCom
        :param files_com: The files communication object
        :type files_com: ClientCom
        """
        self.RELATIVE_BUTTON_SIZE = 0.04
        self.RELATIVE_SIZE = 0.75  # The relative size of the window to the screen
        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE, wx.DisplaySize()[1] * self.RELATIVE_SIZE

        super(MainFrame, self).__init__(parent, title=title, size=size)

        self.SetIcon(wx.Icon("assets/strife_logo_round.ico", wx.BITMAP_TYPE_ICO))

        self.general_com = general_com
        self.chats_com = chats_com
        self.files_com = files_com

        self.login_panel = login_gui.LoginPanel(self)
        self.register_panel = login_gui.RegisterPanel(self)
        self.main_panel = None

        self.panel_switcher = gui_util.PanelsSwitcher(self, [self.login_panel, self.register_panel])

        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Add the app icon to the system tray
        icon = wx.Icon('assets\\strife_logo.ico', wx.BITMAP_TYPE_ICO)
        self.taskbar_icon = wx.adv.TaskBarIcon()
        self.taskbar_icon.SetIcon(icon, 'Strife')
        # Set the taskbar icon to open the GUI when left-clicked
        self.taskbar_icon.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, lambda event: self.Show())
        # Bind the taskbar icon to a function on right-click
        self.taskbar_icon.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.onTrayIconRightClick)

        pub.subscribe(self.onConnectionLost, 'server_connection_lost')
        pub.subscribe(self.onConnection, 'server_connection_established')

    def onTrayIconRightClick(self, event):
        """
        Called when the taskbar icon is right-clicked
        :param event: The event
        :return: -
        """
        # Create a menu with options to show the window, exit the program.
        menu = wx.Menu()
        menu.Append(1, "Open Strife")
        menu.Append(2, "Exit")
        # Bind the menu options to functions
        menu.Bind(wx.EVT_MENU, lambda e: self.Show(), id=1)
        menu.Bind(wx.EVT_MENU, self.exit_program, id=2)
        # Show the menu
        self.taskbar_icon.PopupMenu(menu)

    def exit_program(self, event):
        """
        Called when the program is exited
        :param event: The event
        :return: -
        """
        self.taskbar_icon.Destroy()
        self.close_app()

    def onConnectionLost(self):
        """
        Called when the connection to the server is lost
        :return: None
        """
        wx.MessageBox('Connection to the server was lost', 'Connection lost', wx.OK | wx.ICON_ERROR)
        self.close_app()

    def onConnection(self):
        """
        Called when the connection to the server is established
        :return: None
        """
        if self.general_com.running and self.chats_com.running and self.files_com.running:
            self.Enable()

    def move_to_main(self):
        """
        Moves to the main panel
        :return: -
        """
        self.main_panel = MainPanel(self)
        self.panel_switcher.add_panel(self.main_panel)
        self.panel_switcher.Show(self.main_panel)

    def logout(self):
        self.login_panel.password_input.SetValue('')
        self.login_panel.username_input.SetValue('')
        self.register_panel.password_input.SetValue('')
        self.register_panel.username_input.SetValue('')
        self.panel_switcher.Show(self.login_panel)
        self.Disable()

    def onClose(self, event):
        """
        Called when the user presses the close button
        :param event: The wx event
        :type event: wx.Event
        :return: -
        """
        self.taskbar_icon.ShowBalloon('Strife', 'Strife is still running in the background', 1)
        self.Hide()
        event.Veto()

    def close_app(self):
        """
        Closes the application
        :return: -
        """
        # Close the communication objects
        self.general_com.close()
        self.chats_com.close()
        self.files_com.close()
        # Close the taskbar icon
        self.taskbar_icon.Destroy()
        # Delete the keys
        KeysManager.last_password = None
        KeysManager.chats_keys = {}
        wx.GetApp().ExitMainLoop()


async def update_pic_async(user):
    """
    Updates the user's profile picture
    :param user: The user
    :type user: User
    :return: -
    """
    await user.update_pic()


def f():
    threading.Thread(target=os.system, args=('start assets/secret.mp4',)).start()
