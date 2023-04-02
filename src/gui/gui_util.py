import hashlib
import os
import pyaudio
import threading
import time
from src.core.client_protocol import Protocol
import wx
from typing import List
from wx.lib.scrolledpanel import ScrolledPanel
from pubsub import pub
import src.gui.main_gui as main_gui
from src.handlers.file_handler import FileHandler
from src.core.keys_manager import KeysManager
from src.core.cryptions import AESCipher
import base64
from src.call.video_call import VideoCall
from src.call.voice_call import VoiceCall


STRIFE_BACKGROUND_COLOR = wx.Colour(0, 53, 69)
MAX_PARTICIPANTS = 6


class User:
    # This is a class variable that will hold the currently active user object.
    # It is initialized to None.
    this_user = None
    audio = pyaudio.PyAudio()

    def __init__(self, username='NoUser', status='', chat_id=-1):
        """
        This is the constructor for the User class.

        :param username: A string representing the user's name.
        :type username: str
        :param status: A string representing the user's status.
        :type status: str
        :param chat_id: An integer representing the user's chat ID.
        :type chat_id: int
        """
        # Initialize the instance variables with the provided values.
        self.username = username
        self.status = status
        self.pic = wx.Image('assets/group_pic.png', wx.BITMAP_TYPE_ANY)
        self.video_frame = None
        self.audio_output = None
        self.last_update = 0
        self.MAX_TIMEOUT = 3
        self.chat_id = chat_id
        self.call_on_update = []
        # Call the update_pic() method to update the user's profile picture.
        self.update_pic()

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, User):
            return self.username == __value.username
        
    def __str__(self):
        return f"Username: {self.username}; status: {self.status}; Chatid: {self.chat_id}"

    def update_pic(self):
        """
        This method updates the user's profile picture.

        :return: None
        :rtype: None
        """
        # Get the path to the user's profile picture.
        path = FileHandler.get_pfp_path(self.username)
        # If a path is found, set the user's profile picture to the image at that path.
        if path:
            self.pic = wx.Image(path, wx.BITMAP_TYPE_ANY)

        # Call each function in the call_on_update list.
        # This list is used to update the user's profile picture when it changes.
        for func in self.call_on_update:
            try:
                func()
            except Exception:
                self.call_on_update.remove(func)

    def update_status(self, status):
        self.status = status
        for func in self.call_on_update:
            try:
                func()
            except Exception:
                self.call_on_update.remove(func)

    def add_func_on_update(self, func):
        """
        This method adds a function to the call_on_update list.

        :param func: The function to be added.
        :type func: function
        :return: None
        :rtype: None
        """
        self.call_on_update.append(func)

    def update_video(self, frame):
        """
        This method updates the user's video frame.

        :param frame: The new video frame.
        :type frame: numpy.ndarray
        :return: None
        :rtype: None
        """
        self.video_frame = frame
        self.last_update = time.time()

    def get_frame(self):
        """
        This method returns the user's current video frame.

        :return: The current video frame.
        :rtype: numpy.ndarray
        """
        # Get the current video frame.
        frame = self.video_frame
        # If there is no video frame or the last update was more than MAX_TIMEOUT seconds ago,
        # return the user's profile picture as a bitmap.
        if frame is None or time.time() - self.last_update > self.MAX_TIMEOUT:
            print('yes video no')
            frame = self.pic.ConvertToBitmap()

        return frame
    
    def update_audio(self, audio_frame):
        if not self.audio_output:
            self.audio_output = User.audio.open(format=VoiceCall.FORMAT, channels=VoiceCall.CHANNELS, rate=VoiceCall.RATE, output=True,
                                                frames_per_buffer=VoiceCall.CHUNK)
        self.audio_output.write(audio_frame)


class UserBox(wx.Panel):
    def __init__(self, parent, user: User, align_right=False, onClick=None, pic_size=6):
        """
        Initializes the UserBox object.

        :param parent: Parent object that this UserBox is attached to
        :type parent: wx.Panel
        :param user: User object to display in the UserBox
        :type user: User
        :param align_right: Whether to align the UserBox to the right or not
        :type align_right: bool
        :param onClick: Function to be called when UserBox is clicked
        :type onClick: function
        """
        super(UserBox, self).__init__(parent)

        # Define the relative size of the profile picture
        self.RELATIVE_PIC_SIZE = 0.04 * pic_size/6

        # Store the parent and user objects
        self.parent = parent
        self.user = user

        # Add function to update the profile picture when it is changed
        self.user.add_func_on_update(self.onUpdate)

        # Store the onClick function
        self.onClick = onClick

        # Bind the handle_click function to the left mouse button down event
        self.Bind(wx.EVT_LEFT_DOWN, self.handle_click)

        # Create the horizontal sizer for the UserBox
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        # Add vertical sizer that contains the username and status
        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # Add the username to the vertical sizer
        self.username_text = wx.StaticText(self, label=self.user.username)
        self.username_text.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
        self.vsizer.Add(self.username_text, 0, wx.ALIGN_CENTER)

        # Add the status to the vertical sizer
        self.status_text = wx.StaticText(self, label=self.user.status)
        self.status_text.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
        self.vsizer.Add(self.status_text, 0, wx.ALIGN_CENTER)

        if align_right:
            # Add the vertical sizer to the horizontal sizer
            self.sizer.Add(self.vsizer, 0, wx.ALIGN_CENTER)

            # Add a spacer to separate the vertical sizer and the profile picture
            self.sizer.AddSpacer(10)

            # Add the user profile picture to the horizontal sizer
            pic = self.user.pic\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            self.static_pic = wx.StaticBitmap(self, bitmap=bitmap)
            self.static_pic.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
            self.sizer.Add(self.static_pic, 0, wx.ALIGN_CENTER)

        else:
            # Add the user profile picture to the horizontal sizer
            pic = self.user.pic\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            self.static_pic = wx.StaticBitmap(self, bitmap=bitmap)
            self.static_pic.Bind(wx.EVT_LEFT_DOWN, self.handle_click)
            self.sizer.Add(self.static_pic, 0, wx.ALIGN_CENTER)

            # Add a spacer to separate the profile picture and the vertical sizer
            self.sizer.AddSpacer(10)

            # Add the vertical sizer to the horizontal sizer
            self.sizer.Add(self.vsizer, 0, wx.ALIGN_CENTER)

    def handle_click(self, event):
        """
        Handles the click event on the UserBox panel. Calls the function passed as onClick parameter
        with the chat ID of the user associated with the panel, if it exists.

        :param event: The event object
        :type event: wx.Event
        :return: None
        :rtype: None
        """
        if self.onClick:
            self.onClick(self.user.chat_id)

    def onUpdate(self):
        """
        Updates the user profile picture displayed on the UserBox panel.

        :return: None
        :rtype: None
        """
        # Scale the picture to the appropriate size
        pic = self.user.pic \
            .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
        # Create a bitmap from the scaled picture
        bitmap = wx.Bitmap(pic)
        # Set the bitmap as the profile picture displayed on the panel
        self.static_pic.SetBitmap(bitmap)
        # Update the status
        self.status_text.SetLabel(self.user.status)
        # Update the username
        self.username_text.SetLabel(self.user.username)
        # Refresh the panel to show the updated user
        self.Refresh()
        self.Layout()


class SelectFriendDialog(wx.Dialog):
    def __init__(self, parent, friends_list):
        """
        Initializes the dialog window with a list of friends to select from.

        :param parent: the parent window for this dialog
        :type parent: wx.Window
        :param friends_list: a list of friends to select from
        :type friends_list: list
        """
        # Call the parent constructor with the dialog title
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Select Friend")

        # Create the friend choice widget, add member button, and cancel button
        self.friend_choice = wx.Choice(self, wx.ID_ANY, choices=friends_list)
        self.add_member_button = wx.Button(self, wx.ID_ANY, "Add Member")
        self.cancel_button = wx.Button(self, wx.ID_ANY, "Cancel")

        # Bind the add member and cancel button events
        self.add_member_button.Bind(wx.EVT_BUTTON, self.on_add_member)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Initialize the selected friend to None
        self.friend_chosen = None

        # Create a vertical box sizer and add the friend choice, add member, and cancel button widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Select a friend:"), 0, wx.ALL, 10)
        sizer.Add(self.friend_choice, 0, wx.ALL, 10)
        sizer.Add(self.add_member_button, 0, wx.ALL, 10)
        sizer.Add(self.cancel_button, 0, wx.ALL, 10)
        self.SetSizer(sizer)

        # Fit the dialog window to the size of its children and update the layout
        self.Fit()
        self.Layout()

    def on_add_member(self, event):
        """
        Event handler for the add member button. Stores the selected friend and ends the dialog
        with a success code.

        :param event: the event object
        :type event: wx.Event
        :return: None
        """
        # Store the selected friend
        self.friend_chosen = self.friend_choice.GetStringSelection()

        # Show an error message if no friend is selected
        if not self.friend_chosen:
            wx.MessageBox('Please choose a friend to add', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            # End the dialog with a success code
            self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """
        Event handler for the cancel button. Ends the dialog with a cancel code.

        :param event: the event object
        :type event: wx.Event
        :return: None
        """
        # End the dialog with a cancel code
        self.EndModal(wx.ID_CANCEL)


class PanelsSwitcher(wx.BoxSizer):
    """
    A sizer for switching between panels in a parent window.
    """

    def __init__(self, parent, panels):
        """
        Constructor for PanelsSwitcher.

        :param parent: Parent window.
        :type parent: wx.Window
        :param panels: List of panels to switch between.
        :type panels: list of wx.Window
        """
        # Initialize the base class
        wx.BoxSizer.__init__(self)

        # Attach this sizer to the parent window
        parent.SetSizer(self)

        # Save the parent window
        self.parent = parent

        # Save the list of panels
        self.panels = panels

        # Add all the panels into this sizer
        for panel in self.panels:
            self.Add(panel, 1, wx.EXPAND)

        # Show the first panel and hide the rest of the panels
        self.Show(panels[0])

    def add_panel(self, panel):
        """
        Adds a new panel to the list of panels.

        :param panel: Panel to add.
        :type panel: wx.Window
        """
        self.panels.append(panel)
        self.Add(panel, 1, wx.EXPAND)

    def Show(self, panel):
        """
        Shows the given panel and hides the rest of the panels.

        :param panel: Panel to show.
        :type panel: wx.Window
        """
        # For each panel in the list of panels
        for p in self.panels:
            # Show the given panel
            if p == panel:
                p.Show()
            else:
                # and hide the rest of the panels
                p.Hide()

        # Rearrange the window
        self.parent.Layout()


class UsersScrollPanel(ScrolledPanel):
    def __init__(self, parent, align_right=False, on_click=None):
        """
        Initializes an instance of UsersScrollPanel.

        :param parent: The parent object.
        :type parent: wx.Window
        :param align_right: Aligns the user box to the right if True. Default is False.
        :type align_right: bool
        :param on_click: The function that will be called when a user box is clicked. Default is None.
        :type on_click: function
        """
        super(UsersScrollPanel, self).__init__(parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)  # initializes a vertical box sizer
        self.users = []  # list to store UserBox objects
        self.align_right = align_right  # flag to align user box to the right
        self.on_click = on_click  # function to call when user box is clicked
        self.SetupScrolling()  # enables scrolling in the panel

        self.SetSizer(self.sizer)  # sets the sizer for the panel

    def add_user(self, user: User):
        """
        Adds a UserBox object to the panel.

        :param user: The user object to be added.
        :type user: User
        :return: None
        :rtype: None
        """
        user_box = UserBox(self, user, self.align_right, onClick=self.handle_click)  # creates a UserBox object
        self.users.append(user_box)  # adds the UserBox object to the list
        if self.align_right:
            self.sizer.Add(user_box, 0, wx.EXPAND)  # adds the UserBox object to the sizer
        else:
            self.sizer.Add(user_box, 0, wx.EXPAND)

        self.Refresh()  # updates the panel
        self.Layout()  # updates the layout of the panel
        self.SetupScrolling()  # enables scrolling in the panel

    def remove_user(self, username: str):
        """
        Removes a UserBox object from the panel.

        :param username: The username of the UserBox object to be removed.
        :type username: str
        :return: None
        :rtype: None
        """
        index = -1
        for i in range(len(self.users)):
            if self.users[i].user.username == username:
                index = i
                break

        if index != -1:
            self.sizer.Remove(index)
            del self.users[index]

        self.Refresh()  # updates the panel
        self.Layout()  # updates the layout of the panel
        self.SetupScrolling()  # enables scrolling in the panel

    def reset_friends(self):

        for user in self.users.copy():
            self.remove_user(user.user.username)
        self.users = []

    def handle_click(self, chat_id):
        """
        Changes the background color of the clicked UserBox object and calls the on_click function.

        :param chat_id: The chat id of the User object associated with the clicked UserBox object.
        :type chat_id: int
        :return: None
        :rtype: None
        """
        for userbox in self.users:
            if userbox.user.chat_id == chat_id:
                userbox.SetBackgroundColour(wx.Colour(192, 192, 192))  # sets background color
                userbox.Refresh()  # updates the UserBox object
            else:
                userbox.SetBackgroundColour(wx.NullColour)  # removes background color
                userbox.Refresh()  # updates the UserBox object

        if self.on_click:
            self.on_click(chat_id)  # calls the on_click function with the chat id as argument


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent, title='Settings', style=wx.CAPTION)
        self.RELATIVE_SIZE = 0.5
        # The background color of the window
        self.BACKGROUND_COLOR = STRIFE_BACKGROUND_COLOR

        size = (wx.DisplaySize()[0] * self.RELATIVE_SIZE * 0.8, wx.DisplaySize()[1] * self.RELATIVE_SIZE)
        self.SetSize(size)
        self.SetBackgroundColour(self.BACKGROUND_COLOR)
        self.SetForegroundColour(wx.Colour(237, 99, 99))

        self.parent = parent

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.picture_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        self.name_label = wx.StaticText(self, label='Change username:')
        self.name_label.SetFont(font)
        self.name_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(100, 20))
        self.name_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.username_sizer.Add(self.name_label, 1, wx.ALIGN_CENTER)
        self.username_sizer.AddSpacer(10)
        self.username_sizer.Add(self.name_input, 1, wx.ALIGN_CENTER)
        self.username_sizer.AddSpacer(10)
        self.username_sizer.Add(self.name_submit_button, 1, wx.ALIGN_CENTER)

        self.picture_label = wx.StaticText(self, label='Change profile picture:')
        self.picture_label.SetFont(font)
        self.file_picker = wx.FilePickerCtrl(self, style=wx.FLP_OPEN, wildcard="Image files (*.jpg, *.png, "
                                                                               "*.gif)|*.jpg;*.png;*.gif")
        self.pic_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.picture_sizer.Add(self.picture_label, 1, wx.ALIGN_CENTER)
        self.picture_sizer.AddSpacer(10)
        self.picture_sizer.Add(self.pic_submit_button, 1, wx.ALIGN_CENTER)
        self.picture_sizer.AddSpacer(10)
        self.picture_sizer.Add(self.file_picker, 1, wx.ALIGN_CENTER)
        self.pic_submit_button.Bind(wx.EVT_BUTTON, self.onPicChange)

        self.status_label = wx.StaticText(self, label='Change status:')
        self.status_label.SetFont(font)
        self.status_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(100, 20))
        self.status_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.status_sizer.Add(self.status_label, 1, wx.ALIGN_CENTER)
        self.status_sizer.AddSpacer(10)
        self.status_sizer.Add(self.status_input, 1, wx.ALIGN_CENTER)
        self.status_sizer.AddSpacer(10)
        self.status_sizer.Add(self.status_submit_button, 1, wx.ALIGN_CENTER)
        self.status_submit_button.Bind(wx.EVT_BUTTON, self.onStatusChange)

        self.password_label = wx.StaticText(self, label='Change password:')
        self.password_label.SetFont(font)
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

    def onPicChange(self, event):
        pic_path = self.file_picker.GetPath()
        if pic_path == '':
            wx.MessageBox('No file chosen', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            pic_contents = FileHandler.load_file(pic_path)
            b64_contents = base64.b64encode(pic_contents).decode()
            msg = Protocol.change_pfp(b64_contents)
            self.parent.parent.files_com.send_data(msg)

    def onStatusChange(self, event):
        status = self.status_input.GetValue()
        if status == '':
            wx.MessageBox('No status chosen', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            msg = Protocol.change_status(status)
            self.parent.parent.general_com.send_data(msg)


class CallUserPanel(wx.Panel):
    def __init__(self, parent, user):
        """
        Constructor for the CallUserPanel class.

        :param parent: The parent wx.Window object.
        :type parent: wx.Window
        :param user: The user object to display in the panel.
        :type user: User
        :param fps: The number of frames per second for the timer.
        :type fps: int
        """
        super(CallUserPanel, self).__init__(parent)

        # Make the timer stop when the panel is destroyed
        # self.Bind(wx.EVT_WINDOW_DESTROY, lambda event: self.timer.Stop())

        # Set instance variables
        self.user = user
        self.RELATIVE_SIZE = 0.2
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Get the initial frame for the user and set it as a wx.Bitmap object
        self.bmp = self.user.get_frame()
        self.bmp: wx.Bitmap

        # Set up the label for the user's username
        self.label = wx.StaticText(self, label=self.user.username)
        # Set the font, size and color of the label
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(label_font)

        # Bind events to their respective methods
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        """
        Event handler for the wx.EVT_PAINT event.
        This method is called when the panel needs to be redrawn.

        :param evt: The wx.PaintEvent object.
        :type evt: wx.PaintEvent
        """
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_VIRTUAL_AREA)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        """
        Event handler for the wx.EVT_TIMER event.
        This method is called when the timer fires.
        It gets the next frame for the user and refreshes the display.

        :param event: The wx.TimerEvent object.
        :type event: wx.TimerEvent
        """
        # Get the next frame for the user and set it as a wx.Bitmap object
        frame = self.user.get_frame()
        if type(frame) == wx.Bitmap:
            self.bmp = frame
        else:
            self.bmp.CopyFromBuffer(frame)
        # Scale the bitmap to fit the size of the panel
        self.bmp = self.scale_bitmap(self.bmp, self.GetSize()[0], self.GetSize()[1])
        # Refresh the display
        self.Refresh()

    @staticmethod
    def scale_bitmap(bitmap, width, height):
        """
        A static method for scaling a bitmap to a specified width and height.

        :param bitmap: The bitmap to scale.
        :type bitmap: wx.Bitmap
        :param width: The desired width of the scaled bitmap.
        :type width: int
        :param height: The desired height of the scaled bitmap.
        :type height: int
        :return: The scaled bitmap.
        :rtype: wx.Bitmap
        """
        # Convert the bitmap to a wx.Image object
        image = wx.ImageFromBitmap(bitmap)
        # Scale the image
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        # Convert the image back to a wx.Bitmap object
        result = wx.BitmapFromImage(image)
        return result


class CallGrid(wx.GridSizer):
    def __init__(self, parent):
        """
        Initializes a CallGrid object.

        :param parent: A wxPython parent object.
        :type parent: wxPython parent object.
        """
        self.GAP = 10
        self.BORDER_WIDTH = 10

        # Call the parent constructor with the appropriate arguments
        super(CallGrid, self).__init__(MAX_PARTICIPANTS / 2, MAX_PARTICIPANTS / 2, self.GAP)

        # Initialize an empty list to store user panels
        self.users_panels = []

        # Store the parent object
        self.parent = parent

    def add_user(self, user):
        """
        Adds a user panel to the grid.

        :param user: A user object.
        :type user: User object.
        :return: None
        :rtype: None
        """
        # Create a new CallUserPanel object with the provided user and store it in the list
        self.users_panels.append(CallUserPanel(self.parent, user))

        # Add the panel to the grid with the appropriate flags
        self.Add(self.users_panels[-1], 0, wx.EXPAND, self.BORDER_WIDTH)

    def remove_user(self, username):
        """
        Removes a user panel from the grid.

        :param username: The username of the user to remove.
        :type username: str
        :return: None
        :rtype: None
        """
        # Loop through the user panels
        for panel in self.users_panels:
            # Check if the current panel's user has the same username as the one provided
            if panel.user.username == username:
                # Remove the panel from the grid sizer
                index = self.users_panels.index(panel)
                self.Remove(index)
                # Remove the panel from the list and break the loop
                self.users_panels.remove(panel)
                break


class CallWindow(wx.Frame):
    def __init__(self, parent, title, chat_id, key, video=False):
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

        self.is_video = video
        self.key = key
        self.call_members = {}

        self.voice_call = VoiceCall(self, chat_id, key)
        self.video_call = VideoCall(self, chat_id, key) if video else None

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

        pub.subscribe(self.onVoiceInfo, 'voice_info')
        pub.subscribe(self.onVoiceInfo, 'video_info')
        pub.subscribe(self.onVoiceJoined, 'voice_joined')
        pub.subscribe(self.onVideoJoined, 'video_joined')

    
    def onVoiceInfo(self, chat_id, ips, usernames):
        print('voice info', chat_id, ips, usernames)
        if self.voice_call and self.voice_call.chat_id == chat_id:
            self.call_members = dict(zip(ips, usernames))
            print(self.call_members)

    def onVideoInfo(self, chat_id, ips, usernames):
        print('video info', chat_id, ips, usernames)
        if self.video_call and self.video_call.chat_id == chat_id:
            self.call_members = dict(zip(ips, usernames))
            print(self.call_members)

    def onVoiceJoined(self, chat_id, ip, username):
        print('joined', chat_id, ip, username)
        print('my', self.voice_call.chat_id)
        if self.voice_call and self.voice_call.chat_id == chat_id:
            print('if yes')
            self.voice_call.add_user(ip, main_gui.MainPanel.get_user_by_name(username))
            self.call_members[ip] = username

    def onVideoJoined(self, chat_id, ip, username):
        print('joined', chat_id, ip, username)
        if self.video_call and self.video_call.chat_id == chat_id:
            self.video_call.add_user(ip, main_gui.MainPanel.get_user_by_name(username))
            self.call_members[ip] = username

    def get_user_by_ip(self, ip):
        return main_gui.MainPanel.get_user_by_name(self.call_members.get(ip))

    def onMuteToggle(self, event):
        self.voice_call.toggle_mute()

    def onHangup(self, event):
        self.voice_call.terminate()
        if self.is_video:
            self.video_call.terminate()
        print('closing done')
        self.Close()
        print('closed self.')

    def onCameraToggle(self, event):
        if self.is_video:
            self.video_call.toggle_video()


class MessagesPanel(ScrolledPanel):
    def __init__(self, parent):
        super(MessagesPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
        self.MESSAGES_GAP = 10
        self.SetupScrolling()

        self.SetBackgroundColour(wx.Colour(214, 212, 212))
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.sizer)

        self.parent = parent

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
        is_current_user = sender == User.this_user
        chat_message = ChatMessage(self, sender, message, align_right=False)

        # Add the ChatMessage panel to the ChatPanel sizer
        self.sizer.Add(chat_message, 0, wx.EXPAND, border=5)
        self.sizer.AddSpacer(self.MESSAGES_GAP)

        self.Layout()
        self.Refresh()
        self.SetupScrolling()

    def add_text_message_top(self, sender: User, message: str):
        """
        Adds a text message panel to the top of the chat, aligns the message to the left if the sender is not the current user,
        or to the right if it is.
        :param sender: User object representing the sender of the message
        :type sender: User
        :param message: Text message to be displayed
        :type message: str
        :return: None
        """
        # Create a new ChatMessage panel with the sender box and message
        is_current_user = sender == User.this_user
        chat_message = ChatMessage(self, sender, message, align_right=False)

        # Add the ChatMessage panel to the ChatPanel sizer
        self.sizer.PrependSpacer(self.MESSAGES_GAP)
        self.sizer.Prepend(chat_message, 0, wx.EXPAND, border=5)

        self.Layout()
        self.Refresh()
        self.SetupScrolling()

    def add_file_description(self, chat_id, sender: User, file_name: str, file_size: int, file_hash):
        is_current_user = sender == User.this_user
        file_desc = FileDescription(self, chat_id, sender, file_name, file_size, file_hash, align_right=False)

        # Add the ChatMessage panel to the ChatPanel sizer
        self.sizer.Add(file_desc, 0, wx.EXPAND, border=5)
        self.sizer.AddSpacer(self.MESSAGES_GAP)

        self.Layout()
        self.Refresh()
        self.SetupScrolling()

    def add_file_description_top(self, chat_id, sender: User, file_name: str, file_size: int, file_hash):
        is_current_user = sender == User.this_user
        file_desc = FileDescription(self, chat_id, sender, file_name, file_size, file_hash, align_right=False)

        # Add the ChatMessage panel to the ChatPanel sizer
        self.sizer.PrependSpacer(self.MESSAGES_GAP)
        self.sizer.Prepend(file_desc, 0, wx.EXPAND, border=5)

        self.Layout()
        self.Refresh()
        self.SetupScrolling()


    def reset_messages(self):
        count = self.sizer.Clear(True)


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
            # Get the path of the chosen file
            file_path = dialog.GetPath()
            # Load the contents of the file
            file_contents = FileHandler.load_file(file_path)
            # Encode the file contents in base64 format
            b64_contents = base64.b64encode(file_contents).decode()
            # Construct a message to send the file to the server
            msg = Protocol.send_file(self.chat_id, os.path.basename(file_path), b64_contents)
            # Get the file hash
            file_hash = hashlib.sha256(b64_contents.encode()).hexdigest()
            # Send the message to the server
            self.parent.GetParent().parent.parent.files_com.send_data(msg)
            # File description msg
            msg = Protocol.file_description(User.this_user.username, self.chat_id, os.path.basename(file_path), len(file_contents), file_hash)
            # Send the msg to the server
            self.parent.GetParent().parent.parent.chats_com.send_data(msg)

        dialog.Destroy()

    def onMessageSend(self, event):
        raw_message = str(self.message_input.GetValue())
        if raw_message != '':
            try:
                chat_key = KeysManager.get_chat_key(self.chat_id)
            except Exception as e:
                pass
            else:
                encrypted_msg = AESCipher.encrypt(chat_key, raw_message)
                msg = Protocol.send_message(User.this_user.username, self.chat_id, encrypted_msg)
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


class FileDescription(wx.Panel):
        def __init__(self, parent, user: User, chat_id: int, file_name: str, file_size: int, file_hash: str, align_right=False):
            super(FileDescription, self).__init__(parent)
            self.file_name = file_name
            self.file_size = file_size
            self.sender = user
            self.file_hash = file_hash
            self.chat_id = chat_id
            self.parent = parent
            self.GAP = 40
            self.SetBackgroundColour(wx.Colour(194, 194, 194))

            self.sizer = wx.BoxSizer(wx.HORIZONTAL)

            user_box = UserBox(self, user, align_right=align_right)

            if not align_right:
                self.sizer.Add(user_box, 0, wx.ALIGN_LEFT, border=5)
                self.sizer.AddSpacer(self.GAP)

            # Add a label with the file name
            self.file_name_label = wx.StaticText(self, label=file_name)
            self.sizer.Add(self.file_name_label, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER)

            # Add a label with the file size
            self.file_size_label = wx.StaticText(self, label=f'{round(file_size/1000000, 2)} mb')
            self.sizer.Add(self.file_size_label, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER)

            # Add a button to download the file
            self.download_button = wx.Button(self, label='Download')
            self.download_button.Bind(wx.EVT_BUTTON, self.onDownload)
            self.sizer.Add(self.download_button, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER)

            if align_right:
                self.sizer.AddSpacer(self.GAP)
                self.sizer.Add(user_box, 0, wx.ALIGN_RIGHT, border=5)

            self.SetSizer(self.sizer)

        def onDownload(self, event):
            print('requesting file')
            # Construct a message to request the file from the server
            msg = Protocol.request_file(self.file_hash)
            # Send the message to the server
            self.parent.parent.GetParent().parent.parent.general_com.send_data(msg)


class GroupsSwitcher(wx.BoxSizer):
    def __init__(self, parent):
        """

        :param parent:
        :type parent:
        """
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
        self.current_group_id = -1

        pub.subscribe(self.onTextMessage, 'text_message')
        pub.subscribe(self.onFileDescription, 'file_description')
        pub.subscribe(self.onGroupMembers, 'group_members')
        pub.subscribe(self.onChatHistory, 'chat_history')


    def onChatHistory(self, messages):
        chat_id = messages[0]['chat_id']
        self.groups[chat_id][0].reset_messages()

        for msg in messages:
            sender = msg['sender']
            chat_id = msg['chat_id']
            sender_user = main_gui.MainPanel.get_user_by_name(sender)
            try:
                chat_key = KeysManager.get_chat_key(chat_id)
            except Exception:
                print('no chat key for', chat_id)
            else:
                if msg['opname'] == 'text_message':
                    raw_msg = msg['message']
                    decrypted_message = AESCipher.decrypt(chat_key, raw_msg)
                    print('adding on top!', decrypted_message)
                    self.groups[chat_id][0].add_text_message_top(sender_user, decrypted_message)
                else:
                    # File description
                    filename = msg['file_name']
                    file_size = msg['file_size']
                    file_hash = msg['file_hash']
                    self.groups[chat_id][0].add_file_description_top(sender_user, chat_id, filename, file_size, file_hash)

    def onTextMessage(self, sender, chat_id, raw_message):
        """

        :param sender:
        :type sender:
        :param chat_id:
        :type chat_id:
        :param raw_message:
        :type raw_message:
        :return:
        :rtype:
        """
        try:
            chat_key = KeysManager.get_chat_key(chat_id)
        except Exception:
            pass
        else:
            decrypted_message = AESCipher.decrypt(chat_key, raw_message)
            sender_user = main_gui.MainPanel.get_user_by_name(sender)
            self.groups[chat_id][0].add_text_message(sender_user, decrypted_message)

    def onFileDescription(self, chat_id, file_name, file_size, sender, file_hash):
        sender_user = main_gui.MainPanel.get_user_by_name(sender)
        self.groups[chat_id][0].add_file_description(sender_user, chat_id, file_name, file_size, file_hash)


    def onGroupMembers(self, chat_id, usernames):
        self.groups[chat_id][1].reset_friends()
        for username in usernames:
            user = main_gui.MainPanel.get_user_by_name(username)
            self.add_group_member(chat_id, user)

    def add_group(self, group_id, users: List[User]):
        """

        :param group_id:
        :type group_id:
        :param users:
        :type users:
        :return:
        :rtype:
        """
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
        """

        :param event:
        :type event:
        :return:
        :rtype:
        """
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
                self.parent.parent.parent.general_com.send_data(msg)

    def add_group_member(self, group_id, new_member: User):
        """

        :param group_id:
        :type group_id:
        :param new_member:
        :type new_member:
        :return:
        :rtype:
        """
        self.groups[group_id][1].add_user(new_member)

    def reset_groups(self):
        for i in range(len(self.groups_panels.keys())):
            self.Remove(0)
        self.groups_panels = {}
        self.groups = {}

    def Show(self, chat_id):
        """

        :param chat_id:
        :type chat_id:
        :return:
        :rtype:
        """
        # For each panel in the list of panels
        for id_, group_panel in self.groups_panels.items():
            # Show the given panel
            if id_ == chat_id:
                group_panel.Show()
                self.current_group_id = chat_id
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


class FriendRequestsPanel(ScrolledPanel):
    def __init__(self, parent):
        super(FriendRequestsPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
        self.parent = parent
        self.SetupScrolling()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.friend_requests = []

    def add_friend_request(self, adder: User):
        adder_box = UserBox(self, user=adder, pic_size=5)
        add_button = wx.Button(self, label='approve', name=adder.username)
        add_button.Bind(wx.EVT_BUTTON, self.onRequestClick)
        reject_button = wx.Button(self, label='reject', name=adder.username)
        reject_button.Bind(wx.EVT_BUTTON, self.onRequestClick)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer.Add(add_button, 0, wx.EXPAND)
        buttons_sizer.Add(reject_button, 0, wx.EXPAND)

        request_sizer = wx.BoxSizer(wx.HORIZONTAL)
        request_sizer.Add(adder_box, 0, wx.ALIGN_LEFT)
        request_sizer.AddSpacer(10)
        request_sizer.Add(buttons_sizer, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER)
        self.sizer.Add(request_sizer)
        self.friend_requests.append(adder)
        self.SetupScrolling()
        self.Refresh()
        self.Layout()

    def onRequestClick(self, event):
        username = event.GetEventObject().GetName()
        label = event.GetEventObject().GetLabel()
        approved = label == 'approve'
        index = -1
        for adder in self.friend_requests:
            if adder.username == username:
                index = self.friend_requests.index(adder)
                self.friend_requests.remove(adder)
                break
        if index != -1:
            sizer = self.sizer.GetItem(index)
            sizer.DeleteWindows()
            self.sizer.Remove(index)
            self.Layout()
            self.SetupScrolling()

        # Send the friend request approve/reject message
        msg = Protocol.accept_friend_request(username, approved)
        self.parent.parent.general_com.send_data(msg)


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














