import threading
import time
from src.core.client_protocol import Protocol
import wx
from typing import List
from wx.lib.scrolledpanel import ScrolledPanel
from pubsub import pub
import main_gui
from src.handlers.file_handler import FileHandler
from src.core.keys_manager import KeysManager


STRIFE_BACKGROUND_COLOR = wx.Colour(0, 53, 69)
MAX_PARTICIPANTS = 6


class User:
    this_user = None

    def __init__(self, username='NoUser', status='', chat_id=-1):
        self.username = username
        self.status = status
        self.pic = wx.Image('assets/strife_logo.png', wx.BITMAP_TYPE_ANY)
        self.video_frame = None
        self.last_update = 0
        self.MAX_TIMEOUT = 3
        self.chat_id = chat_id
        self.call_on_update = []
        self.update_pic()

    def update_pic(self):
        path = FileHandler.get_pfp_path(self.username)
        if path:
            self.pic = wx.Image(path, wx.BITMAP_TYPE_ANY)

        for func in self.call_on_update:
            func()

    def add_func_on_update(self, func):
        self.call_on_update.append(func)

    def update_video(self, frame):
        self.video_frame = frame
        self.last_update = time.time()

    def get_frame(self):
        frame = self.video_frame
        if frame is None or time.time() - self.last_update > self.MAX_TIMEOUT:
            frame = self.pic.ConvertToBitmap()

        return frame


class UserBox(wx.Panel):
    def __init__(self, parent, user: User, align_right=False, onClick=None):
        super(UserBox, self).__init__(parent)
        self.RELATIVE_PIC_SIZE = 0.04

        self.parent = parent
        self.user = user
        self.user.add_func_on_update(self.onPicUpdate)

        self.onClick = onClick

        self.Bind(wx.EVT_LEFT_DOWN, self.handle_click)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        # Add vertical sizer that contains the username and status
        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # Add the username to it
        username_text = wx.StaticText(self, label=self.user.username)
        username_text.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
        self.vsizer.Add(username_text, 0, wx.EXPAND)

        # Add the status
        status_text = wx.StaticText(self, label=self.user.status)
        status_text.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
        self.vsizer.Add(status_text, 0, wx.EXPAND)

        if align_right:
            # Add the vertical sizer to the sizer
            self.sizer.Add(self.vsizer, 0, wx.ALIGN_CENTER)

            self.sizer.AddSpacer(10)

            # Add user profile picture
            pic = wx.Image(self.user.pic, wx.BITMAP_TYPE_ANY)\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            self.static_pic = wx.StaticBitmap(self, bitmap=bitmap)
            self.static_pic.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
            self.sizer.Add(self.static_pic, 0, wx.ALIGN_CENTER)

        else:
            # Add user profile picture
            pic = self.user.pic\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            self.static_pic = wx.StaticBitmap(self, bitmap=bitmap)
            self.static_pic.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
            self.sizer.Add(self.static_pic, 0, wx.ALIGN_CENTER)

            self.sizer.AddSpacer(10)

            # Add the vertical sizer to the sizer
            self.sizer.Add(self.vsizer, 0, wx.ALIGN_CENTER)

    def handle_click(self, event):
        if self.onClick:
            self.onClick(self.user.chat_id)

    def onPicUpdate(self):
        pic = self.user.pic \
            .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
        bitmap = wx.Bitmap(pic)
        self.static_pic.SetBitmap(bitmap)
        self.Refresh()


class SelectFriendDialog(wx.Dialog):
    def __init__(self, parent, friends_list):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Select Friend")

        self.friend_choice = wx.Choice(self, wx.ID_ANY, choices=friends_list)
        self.add_member_button = wx.Button(self, wx.ID_ANY, "Add Member")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")

        self.add_member_button.Bind(wx.EVT_BUTTON, self.on_add_member)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.friend_chosen = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Select a friend:"), 0, wx.ALL, 10)
        sizer.Add(self.friend_choice, 0, wx.ALL, 10)
        sizer.Add(self.add_member_button, 0, wx.ALL, 10)
        sizer.Add(self.cancel_button, 0, wx.ALL, 10)
        self.SetSizer(sizer)

        self.Fit()
        self.Layout()

    def on_add_member(self, event):
        # Do something when "Add Member" button is clicked
        self.friend_chosen = self.friend_choice.GetStringSelection()
        if not self.friend_chosen:
            wx.MessageBox('Please choose a friend to add', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class PanelsSwitcher(wx.BoxSizer):
    # The constructor a parent window
    # and a list of panels for switch between them
    def __init__(self, parent, panels):
        # Initialize the base class
        wx.BoxSizer.__init__(self)
        # Attach this sizer to the parent window
        parent.SetSizer(self)
        # Save the parent windows
        self.parent = parent
        # Save the list of panels
        self.panels = panels
        # Add all the panels into this sizer
        for panel in self.panels:
            self.Add(panel, 1, wx.EXPAND)
        # Show the first panel and hide the rest of panels
        self.Show(panels[0])

    def add_panel(self, panel):
        self.panels.append(panel)
        self.Add(panel, 1, wx.EXPAND)

    # Show some panel and hide the rest of panels
    def Show(self, panel):
        # For each panel in the list of panels
        for p in self.panels:
            # Show the given panel
            if p == panel:
                p.Show()
            else:
                # and hide the rest
                p.Hide()
        # Rearrange the window
        self.parent.Layout()


class UsersScrollPanel(ScrolledPanel):
    def __init__(self, parent, align_right=False, on_click=None):
        super(UsersScrollPanel, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.users = []
        self.align_right = align_right
        self.on_click = on_click
        self.SetupScrolling()

        self.SetSizer(self.sizer)

    def add_user(self, user: User):
        user_box = UserBox(self, user, self.align_right, onClick=self.handle_click)
        self.users.append(user_box)
        if self.align_right:
            self.sizer.Add(user_box, 0, wx.EXPAND)
        else:
            self.sizer.Add(user_box, 0, wx.EXPAND)

        self.Refresh()
        self.Layout()
        self.SetupScrolling()

    def remove_user(self, username: str):
        index = -1
        for i in range(len(self.users)):
            if self.users[i].username == username:
                index = i
                break

        if index != -1:
            self.sizer.Remove(index)

        self.Refresh()
        self.Layout()
        self.SetupScrolling()

    def handle_click(self, chat_id):
        for userbox in self.users:
            if userbox.user.chat_id == chat_id:
                userbox.SetBackgroundColour(wx.Colour(192, 192, 192))
                userbox.Refresh()
            else:
                userbox.SetBackgroundColour(wx.NullColour)
                userbox.Refresh()

        if self.on_click:
            self.on_click(chat_id)


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, title='Settings', style=wx.CAPTION)
        self.RELATIVE_SIZE = 0.5
        # The background color of the window
        self.BACKGROUND_COLOR = STRIFE_BACKGROUND_COLOR

        size = (wx.DisplaySize()[0] * self.RELATIVE_SIZE * 0.8, wx.DisplaySize()[1] * self.RELATIVE_SIZE)
        self.SetSize(size)
        self.SetBackgroundColour(self.BACKGROUND_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.picture_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.name_label = wx.StaticText(self, label='Change username:')
        self.name_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(100, 20))
        self.name_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.username_sizer.Add(self.name_label, 1, wx.ALIGN_CENTER)
        self.username_sizer.AddSpacer(10)
        self.username_sizer.Add(self.name_input, 1, wx.ALIGN_CENTER)
        self.username_sizer.AddSpacer(10)
        self.username_sizer.Add(self.name_submit_button, 1, wx.ALIGN_CENTER)

        self.picture_label = wx.StaticText(self, label='Change profile picture:')
        self.file_picker = wx.FilePickerCtrl(self, style=wx.FLP_OPEN, wildcard="Image files (*.jpg, *.png, "
                                                                               "*.gif)|*.jpg;*.png;*.gif")
        self.pic_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.picture_sizer.Add(self.picture_label, 1, wx.ALIGN_CENTER)
        self.picture_sizer.AddSpacer(10)
        self.picture_sizer.Add(self.file_picker, 1, wx.ALIGN_CENTER)
        self.picture_sizer.AddSpacer(10)
        self.picture_sizer.Add(self.pic_submit_button, 1, wx.ALIGN_CENTER)

        self.status_label = wx.StaticText(self, label='Change status:')
        self.status_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(100, 20))
        self.status_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.status_sizer.Add(self.status_label, 1, wx.ALIGN_CENTER)
        self.status_sizer.AddSpacer(10)
        self.status_sizer.Add(self.status_input, 1, wx.ALIGN_CENTER)
        self.status_sizer.AddSpacer(10)
        self.status_sizer.Add(self.status_submit_button, 1, wx.ALIGN_CENTER)

        self.password_label = wx.StaticText(self, label='Change password:')
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_LEFT, size=(100, 20))
        self.pass_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.password_sizer.Add(self.password_label, 1, wx.ALIGN_CENTER)
        self.password_sizer.AddSpacer(10)
        self.password_sizer.Add(self.password_input, 1, wx.ALIGN_CENTER)
        self.password_sizer.AddSpacer(10)
        self.password_sizer.Add(self.pass_submit_button, 1, wx.ALIGN_CENTER)

        self.back_button = wx.Button(self, label='Back', size=(100, 50))
        self.back_button.Bind(wx.EVT_BUTTON, self.onBack)

        self.sizer.Add(self.username_sizer, 1, wx.ALIGN_CENTER)
        self.sizer.Add(self.password_sizer, 1, wx.ALIGN_CENTER)
        self.sizer.Add(self.picture_sizer, 1, wx.ALIGN_CENTER)
        self.sizer.Add(self.status_sizer, 1, wx.ALIGN_CENTER)
        self.sizer.Add(self.back_button, 1, wx.ALIGN_CENTER)

        self.SetSizer(self.sizer)

    def onBack(self, event):
        self.Close()


class CallUserPanel(wx.Panel):
    def __init__(self, parent, user, fps=30):
        super(CallUserPanel, self).__init__(parent)

        # Make the timer stop when the panel is destroyed
        self.Bind(wx.EVT_WINDOW_DESTROY, lambda event: self.timer.Stop())

        self.user = user
        self.RELATIVE_SIZE = 0.2
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.bmp = self.user.get_frame()
        self.bmp: wx.Bitmap

        # Text
        self.label = wx.StaticText(self, label=self.user.username)
        # Set the font, size and color of the label
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(label_font)

        self.timer = wx.Timer(self)
        self.timer.Start(1000.0 / fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_VIRTUAL_AREA)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        frame = self.user.get_frame()
        if type(frame) == wx.Bitmap:
            self.bmp = frame
        else:
            self.bmp.CopyFromBuffer(frame)
        self.bmp = self.scale_bitmap(self.bmp, self.GetSize()[0], self.GetSize()[1])
        self.Refresh()

    @staticmethod
    def scale_bitmap(bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result


class CallGrid(wx.GridSizer):
    def __init__(self, parent):
        self.GAP = 10
        self.BORDER_WIDTH = 10

        super(CallGrid, self).__init__(MAX_PARTICIPANTS/2, MAX_PARTICIPANTS/2, self.GAP)
        self.users_panels = []
        self.parent = parent

    def add_user(self, user):
        self.users_panels.append(CallUserPanel(self.parent, user))
        self.Add(self.users_panels[-1], 0, wx.EXPAND, self.BORDER_WIDTH)

    def remove_user(self, username):
        for panel in self.users_panels:
            if panel.user.username == username:
                self.users_panels.remove(panel)
                break


class CallWindow(wx.Frame):
    def __init__(self, parent, title, video=False):
        super(CallWindow, self).__init__(parent, name=title)
        self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX
                                ^ wx.MAXIMIZE_BOX ^ wx.SYSTEM_MENU ^ wx.CLOSE_BOX)

        self.MUTE_BUTTON_IMAGE = wx.Image("assets/mute.png", wx.BITMAP_TYPE_ANY)
        self.MUTED_BUTTON_IMAGE = wx.Image("assets/mute.png", wx.BITMAP_TYPE_ANY)
        self.LEAVE_BUTTON_IMAGE = wx.Image("assets/leave.png", wx.BITMAP_TYPE_ANY)
        self.CAMERA_ON_IMAGE = wx.Image("assets/turn_off_camera.png", wx.BITMAP_TYPE_ANY)
        self.CAMERA_OFF_IMAGE = wx.Image("assets/turn_on_camera.png", wx.BITMAP_TYPE_ANY)

        self.RELATIVE_BUTTON_SIZE = 0.1

        self.RELATIVE_SIZE = 0.6
        # The background color of the window
        self.BACKGROUND_COLOR = STRIFE_BACKGROUND_COLOR

        size = (wx.DisplaySize()[0] * self.RELATIVE_SIZE, wx.DisplaySize()[1] * self.RELATIVE_SIZE)
        self.SetSize(size)
        self.SetBackgroundColour(self.BACKGROUND_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.call_grid = CallGrid(self)

        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)

        bit = self.MUTE_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.mute_button = wx.BitmapButton(self, bitmap=bit)
        self.mute_button.Bind(wx.EVT_BUTTON, self.onMuteToggle)

        bit = self.LEAVE_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.leave_call_button = wx.BitmapButton(self, bitmap=bit)
        self.leave_call_button.Bind(wx.EVT_BUTTON, self.onHangup)

        bit = self.CAMERA_ON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.camera_button = wx.BitmapButton(self, bitmap=bit)
        self.camera_button.Bind(wx.EVT_BUTTON, self.onCameraToggle)

        self.toolbar.Add(self.mute_button, 1, wx.ALIGN_CENTER)
        self.toolbar.Add(self.leave_call_button, 1, wx.ALIGN_CENTER)
        self.toolbar.Add(self.camera_button, 1, wx.ALIGN_CENTER)

        self.sizer.Add(self.call_grid, 3, wx.EXPAND)
        self.sizer.Add(self.toolbar, 1, wx.ALIGN_CENTER)

        self.SetSizer(self.sizer)

    def onMuteToggle(self, event):
        # TODO: handle mute, change icon
        pass

    def onHangup(self, event):
        # TODO: handle logic stuff
        self.Close()

    def onCameraToggle(self, event):
        # TODO: handle camera, change icon
        pass


class MessagesPanel(ScrolledPanel):
    def __init__(self, parent):
        super(MessagesPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
        self.MESSAGES_GAP = 10
        self.SetupScrolling()

        self.SetBackgroundColour(wx.Colour(214, 212, 212))
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.sizer)

    def add_text_message(self, sender: User, message: str):
        """
        Adds a text message panel to the chat, aligns the message to the left if the sender is not the current user,
        or to the right if it is.
        :param sender: User object representing the sender of the message
        :type sender: User
        :param message: Text message to be displayed
        :type message: str
        :return: None
        """
        # Create a new ChatMessage panel with the sender box and message
        is_current_user = False  # TEMP
        chat_message = ChatMessage(self, sender, message, align_right=is_current_user)

        # Add the ChatMessage panel to the ChatPanel sizer
        self.sizer.Add(chat_message, 0, wx.EXPAND, border=5)
        self.sizer.AddSpacer(self.MESSAGES_GAP)
        self.Layout()


class ChatTools(wx.Panel):
    def __init__(self, parent, chat_id):
        super(ChatTools, self).__init__(parent)
        self.parent = parent
        self.MAX_MESSAGE_LENGTH = 150
        self.MAX_LINES = 3
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chat_id = chat_id

        self.message_input = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        # Create a font object with the desired font size
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        # Set the font on the text control
        self.message_input.SetFont(font)
        self.message_input.SetMaxLength(self.MAX_MESSAGE_LENGTH)

        self.send_file_button = wx.Button(self, label='')
        file_image = wx.Image("assets/file.png", wx.BITMAP_TYPE_ANY)
        file_image = resize_image(file_image, self.send_file_button.GetSize()[0]*2, self.send_file_button.GetSize()[1]*2)
        self.send_file_button.SetBitmap(file_image.ConvertToBitmap())
        self.send_file_button.Bind(wx.EVT_BUTTON, self.on_file_choose)

        self.send_button = wx.Button(self, label='')
        file_image = wx.Image("assets/send.png", wx.BITMAP_TYPE_ANY)
        file_image = resize_image(file_image, self.send_file_button.GetSize()[0]*3, self.send_file_button.GetSize()[1]*3)
        self.send_button.SetBitmap(file_image.ConvertToBitmap())
        self.send_button.Bind(wx.EVT_BUTTON, self.onMessageSend)

        self.sizer.Add(self.send_file_button, 1, wx.EXPAND)
        self.sizer.Add(self.message_input, 5, wx.EXPAND)
        self.sizer.Add(self.send_button, 2, wx.EXPAND)

        self.SetSizer(self.sizer)

    def on_file_choose(self, event):
        wildcard = 'All files (*.*)|*.*'  # Filter file types to show
        dialog = wx.FileDialog(None, message='Choose a file', wildcard=wildcard, style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            # TODO: Do something with the selected file path
        dialog.Destroy()

    def onMessageSend(self, event):
        raw_message = str(self.message_input.GetValue())
        if raw_message != '':
            # TODO: encrypt raw message
            msg = Protocol.send_message(User.this_user.username, self.chat_id, raw_message)
            self.parent.GetParent().parent.parent.chats_com.send_data(msg)
            self.message_input.Clear()


class ChatMessage(wx.Panel):
    """
    A panel for displaying a chat message- The user box alongside the text message split into lines
    """
    def __init__(self, parent, user: User, message: str, align_right=False):
        super(ChatMessage, self).__init__(parent)

        self.GAP = 20
        self.SetBackgroundColour(wx.Colour(194, 194, 194))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_box = UserBox(self, user, align_right=align_right)

        # Add the user box to the left of the ChatMessage panel if the message is not from the current user
        if not align_right:
            self.sizer.Add(user_box, 0, wx.ALIGN_LEFT, border=5)

        # Create a wx.StaticText widget with the message and add it to the ChatMessage panel
        message_label = wx.StaticText(self, label=message)

        if align_right:
            # Add the message sizer to the ChatMessage panel
            self.sizer.Add(message_label, 0, wx.ALIGN_RIGHT)
        else:
            self.sizer.AddSpacer(self.GAP)
            # Add the message sizer to the ChatMessage panel
            self.sizer.Add(message_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER)

        # Add the user box to the right of the ChatMessage panel if the message is from the current user
        if align_right:
            self.sizer.AddSpacer(self.GAP)
            self.sizer.Add(user_box, 0, wx.ALIGN_RIGHT, border=5)

        self.SetSizer(self.sizer)
        self.Layout()


class GroupsSwitcher(wx.BoxSizer):
    def __init__(self, parent):
        # Initialize the base class
        wx.BoxSizer.__init__(self)
        # Attach this sizer to the parent window
        parent.SetSizer(self)
        # Save the parent windows
        self.parent = parent
        # A dict of all the groups panels where the key is the group id
        self.groups_panels = {}
        self.groups = {}
        self.add_member_dialog = SelectFriendDialog(self.parent,
                                                    [friend.username for friend in main_gui.MainPanel.my_friends])

        pub.subscribe(self.onTextMessage, 'text_message')

    def onTextMessage(self, sender, chat_id, raw_message):
        sender_user = main_gui.MainPanel.get_user_by_name(sender)
        print('adding msg', raw_message)
        self.groups[chat_id][0].add_text_message(sender_user, raw_message)

    def add_group(self, group_id, users: List[User]):
        group_panel = wx.Panel(self.parent)

        group_members = UsersScrollPanel(group_panel)
        group_messages = MessagesPanel(group_panel)
        chat_tools = ChatTools(group_panel, group_id)
        chat_sizer = wx.BoxSizer(wx.VERTICAL)
        chat_sizer.Add(group_messages, 6, wx.EXPAND)
        chat_sizer.Add(chat_tools, 1, wx.EXPAND)
        add_group_member_button = wx.Button(group_panel, label='Add group member', id=group_id)
        add_group_member_button.Bind(wx.EVT_BUTTON, self.onGroupMemberAdd)

        self.groups[group_id] = (group_messages, group_members, chat_tools)

        for user in users:
            group_members.add_user(user)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(chat_sizer, 3, wx.EXPAND)

        right_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        right_bar_sizer.Add(group_members, 6, wx.EXPAND)
        right_bar_sizer.Add(add_group_member_button, 1, wx.EXPAND)

        sizer.Add(right_bar_sizer, 1, wx.EXPAND)
        group_panel.SetSizer(sizer)

        self.Add(group_panel, 1, wx.EXPAND)
        group_panel.Hide()

        self.groups_panels[group_id] = group_panel

    def onGroupMemberAdd(self, event):
        group_id = event.GetId()
        friends_usernames = [friend.username for friend in main_gui.MainPanel.my_friends]
        group_key = KeysManager.get_chat_key(group_id)
        # Check if the window is already shown
        if not self.add_member_dialog.IsShown():
            # Create a new dialog
            self.add_member_dialog = SelectFriendDialog(self.parent, friends_usernames)
            # Get the return value of the dialog
            val = self.add_member_dialog.ShowModal()
            # If the dialog wasn't canceled
            if val == wx.ID_OK:
                # Get the chosen friend username
                friend_username = self.add_member_dialog.friend_chosen
                # Construct a message to add the friend to the group
                msg = Protocol.add_member_to_group(group_id, friend_username, group_key)
                # Send the message to the server
                self.parent.general_com.send_data(msg)

    def add_group_member(self, group_id, new_member: User):
        self.groups[group_id][1].add_user(new_member)

    def Show(self, chat_id):
        # For each panel in the list of panels
        for id_, group_panel in self.groups_panels.items():
            # Show the given panel
            if id_ == chat_id:
                group_panel.Show()
            else:
                # and hide the rest
                group_panel.Hide()
        # Rearrange the window
        self.parent.Layout()


class GroupsPanel(wx.Panel):
    def __init__(self, parent):
        super(GroupsPanel, self).__init__(parent)
        self.parent = parent

        self.sizer = GroupsSwitcher(self)
        self.SetSizer(self.sizer)


class CreateGroupDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Create New Group")

        self.parent = parent

        self.group_name = None

        # Create the text control for entering the group name
        self.name_textctrl = wx.TextCtrl(self)

        # Create the "Create" button
        create_button = wx.Button(self, label="Create")
        create_button.Bind(wx.EVT_BUTTON, self.on_create)

        # Create the "Cancel" button
        cancel_button = wx.Button(self, label="Cancel")
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Create a sizer to lay out the controls vertically
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Group name:"), flag=wx.ALL, border=5)
        sizer.Add(self.name_textctrl, flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=5)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(create_button, flag=wx.ALL, border=5)
        button_sizer.Add(cancel_button, flag=wx.ALL, border=5)
        sizer.Add(button_sizer, flag=wx.EXPAND|wx.ALL, border=5)

        # Set the sizer for the dialog
        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_create(self, event):
        # Handle the "Create" button click
        self.group_name = self.name_textctrl.GetValue()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        # Handle the "Cancel" button click
        self.EndModal(wx.ID_CANCEL)


class AddFriendDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title='Add a new friend')

        panel = wx.Panel(self)

        self.friend_username = None

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Enter username:')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)

        self.friend_username = wx.TextCtrl(panel)
        hbox1.Add(self.friend_username, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        btn_add = wx.Button(panel, label='Add')
        btn_add.Bind(wx.EVT_BUTTON, self.OnAdd)
        hbox2.Add(btn_add)

        btn_cancel = wx.Button(panel, label='Cancel')
        btn_cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        hbox2.Add(btn_cancel, flag=wx.LEFT, border=5)

        vbox.Add(hbox2, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        vbox.Fit(self)
        self.Centre()

    def OnAdd(self, event):
        friend_username = self.friend_username.GetValue()
        if friend_username:
            self.friend_username = friend_username
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox('Please enter a username.', 'Error', wx.OK | wx.ICON_ERROR)

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


def resize_image(image, target_width, target_height):
    width, height = image.GetSize()
    aspect_ratio = width / float(height)

    if aspect_ratio > 1:
        # landscape orientation
        new_width = target_width
        new_height = int(round(new_width / aspect_ratio))
    else:
        # portrait orientation or square
        new_height = target_height
        new_width = int(round(new_height * aspect_ratio))

    image = image.Scale(new_width, new_height, quality=wx.IMAGE_QUALITY_HIGH)
    return image














