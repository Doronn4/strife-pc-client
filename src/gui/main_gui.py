import os
import sys

import wx
import wx.adv
import src.gui.gui_util as gui_util
import src.gui.login_gui as login_gui
from src.core.client_protocol import Protocol
from pubsub import pub
import wx.lib.mixins.inspection
from src.handlers.file_handler import FileHandler
from src.core.keys_manager import KeysManager


class MainPanel(wx.Panel):
    known_users = []
    my_friends = []

    def __init__(self, parent):
        super(MainPanel, self).__init__(parent)
        self.STRIFE_LOGO_IMAGE = wx.Image("assets/strife_logo.png", wx.BITMAP_TYPE_ANY)
        self.VOICE_BUTTON_IMAGE = wx.Image("assets/voice.png", wx.BITMAP_TYPE_ANY)
        self.VIDEO_BUTTON_IMAGE = wx.Image("assets/video.png", wx.BITMAP_TYPE_ANY)
        self.LOGOUT_BUTTON_IMAGE = wx.Image("assets/logout.png", wx.BITMAP_TYPE_ANY)
        self.SETTINGS_BUTTON_IMAGE = wx.Image("assets/settings.png", wx.BITMAP_TYPE_ANY)

        self.RELATIVE_BUTTON_SIZE = 0.04
        self.RELATIVE_SIZE = 0.75  # The relative size of the window to the screen

        self.parent = parent

        # Sub windows
        self.settings_window = gui_util.SettingsDialog(self)
        self.voice_call_window = None  # temp ******
        self.video_call_window = None  # temp ******
        self.group_creation_window = gui_util.CreateGroupDialog(self)
        self.add_friend_window = gui_util.AddFriendDialog(self)

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

        self.add_friend_button = wx.Button(self, label='Add friend')
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
        self.load_friends()

    def onUserPic(self, contents, username):
        if username == gui_util.User.this_user.username:
            path = FileHandler.save_pfp(contents, username)
            gui_util.User.this_user.update_pic()
        else:
            path = FileHandler.save_pfp(contents, username)
            MainPanel.get_user_by_name(username).update_pic()

    def onChatsList(self, chats):
        # Reset lists
        MainPanel.my_friends = []
        self.friends_panel.reset_friends()
        self.groups_panel.sizer.reset_groups()

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
                # Add the friend user to the friends panel
                self.friends_panel.add_user(user)
                # Create a group to represent the chat with the friend
                self.groups_panel.sizer.add_group(chat_id, [gui_util.User.this_user, user])
                # Construct a message to request the user's profile pic
                msg = Protocol.request_user_pfp(other_username)
                # Send the message to the server
                self.parent.general_com.send_data(msg)
            else:
                # If it's a group chat
                # Create a user object for the group
                group_user = gui_util.User(username=chat_name, chat_id=chat_id)
                # Add the group's user object to the friends panel
                self.friends_panel.add_user(group_user)
                # Create a new group in the groups panel and add the current user to it
                self.groups_panel.sizer.add_group(chat_id, [gui_util.User.this_user])
                # Send a message to the server requesting a list of the group's members
                msg = Protocol.request_group_members(chat_id)
                self.parent.general_com.send_data(msg)

    def load_friends(self):
        # Request the list of chats
        msg = Protocol.request_chats()
        self.parent.general_com.send_data(msg)

        # Request the current user's profile pic
        msg = Protocol.request_user_pfp(gui_util.User.this_user.username)
        self.parent.general_com.send_data(msg)

    def onAddFriendAnswer(self, is_valid):
        if not is_valid:
            wx.MessageBox("Friend's username doesn't exist", 'Error', wx.OK | wx.ICON_ERROR)
            self.onAddFriend(None)

    def onAddFriend(self, event):
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
                # Construct a message to add a new friend
                msg = Protocol.add_friend(friend_username)
                # Send the message to the server
                self.parent.general_com.send_data(msg)

    def onFriendAdded(self, friend_username, friends_key, chat_id):
        # Request chats list from the server
        msg = Protocol.request_chats()
        self.parent.general_com.send_data(msg)

        KeysManager.add_key(int(chat_id), friends_key)

        # Create a notification for the user
        notification = wx.adv.NotificationMessage('New friend added!', f'you are now friends with {friend_username}',
                                                  self, wx.ICON_INFORMATION)
        notification.Show()

    def onFriendRequest(self, adder_username, is_silent):
        self.friend_requests_panel.add_friend_request(MainPanel.get_user_by_name(adder_username))
        if not is_silent:
            notification = wx.adv.NotificationMessage('New friend request', f'you have a new friend request from {adder_username}',
                                                      self, wx.ICON_INFORMATION)
            notification.Show()

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
        if not self.settings_window.IsShown():
            self.settings_window = gui_util.SettingsDialog(self)
            self.settings_window.Show()

    def check_group_name(self, name) -> str:
        pass

    def onGroupJoin(self, group_name, chat_id):
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

    def onVoice(self, event):
        # TODO: handle logic etc....

        title = 'ifath fans'  # temp

        self.voice_call_window = gui_util.CallWindow(self, title)

        # temp
        for i in range(4):
            self.voice_call_window.call_grid.add_user(gui_util.User('doron'+str(i)))
        # ----
        self.voice_call_window.Show()

    def onVideo(self, event):
        # TODO: handle logic etc....

        title = 'ifath fans'  # temp

        self.video_call_window = gui_util.CallWindow(self, title, video=True)

        # temp
        for i in range(4):
            self.video_call_window.call_grid.add_user(gui_util.User('doron'+str(i)))
        # ----
        self.video_call_window.Show()

    def onLogout(self, event):
        # Handle logging out logic
        pass

    @staticmethod
    def get_user_by_name(username):
        user_found = None
        for user in MainPanel.known_users:
            if user.username == username:
                user_found = user
                break
        if not user_found:
            user_found = gui_util.User(username=username)
            MainPanel.known_users.append(user_found)

        return user_found


class MainFrame(wx.Frame):
    def __init__(self, parent, title, general_com, chats_com, files_com):
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

    def move_to_main(self):
        self.main_panel = MainPanel(self)
        self.panel_switcher.add_panel(self.main_panel)
        self.panel_switcher.Show(self.main_panel)

    def onClose(self, event):
        # TODO: add things
        KeysManager.save_keys()
        event.Skip()


def restart_program():
    python = sys.executable
    os.execl(python, python, 'src/core/main.py')
