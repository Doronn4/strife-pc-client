import wx
from wx.lib.scrolledpanel import ScrolledPanel


# Define the new event type
EVT_LOGIN = wx.NewEventType()
# Define the event binder
EVT_LOGIN_BINDER = wx.PyEventBinder(EVT_LOGIN, 1)
STRIFE_BACKGROUND_COLOR = wx.Colour(0, 53, 69)
MAX_PARTICIPANTS = 6


class LoginEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        super().__init__(eventType, id)
        self.username = ""
        self.password = ""

    def set_credentials(self, username, password):
        self.username = username
        self.password = password


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


class UserBox(wx.BoxSizer):
    def __init__(self, parent, username='NoUser', status='No status', pic='strife_logo.png', align_right=False):
        super(UserBox, self).__init__(wx.HORIZONTAL)
        self.RELATIVE_PIC_SIZE = 0.04

        self.parent = parent
        self.username = username
        self.status = status
        self.pic = pic

        # Add vertical sizer that contains the username and status
        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # Add the username to it
        username_text = wx.StaticText(self.parent, label=self.username)
        self.vsizer.Add(username_text, 1, wx.EXPAND)

        # Add the status
        status_text = wx.StaticText(self.parent, label=self.status)
        self.vsizer.Add(status_text, 1, wx.EXPAND)

        if align_right:
            # Add the vertical sizer to the sizer
            self.Add(self.vsizer, 0, wx.ALIGN_CENTER)

            # Add user profile picture
            pic = wx.Image(self.pic, wx.BITMAP_TYPE_ANY)\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            static_pic = wx.StaticBitmap(self.parent, bitmap=bitmap)
            self.Add(static_pic, 0, wx.ALIGN_CENTER)

        else:
            # Add user profile picture
            pic = wx.Image(self.pic, wx.BITMAP_TYPE_ANY)\
                .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
            bitmap = wx.Bitmap(pic)
            static_pic = wx.StaticBitmap(self.parent, bitmap=bitmap)
            self.Add(static_pic, 0, wx.ALIGN_CENTER)

            # Add the vertical sizer to the sizer
            self.Add(self.vsizer, 0, wx.ALIGN_CENTER)


class UsersScrollPanel(ScrolledPanel):
    def __init__(self, parent, align_right=False):
        super(UsersScrollPanel, self).__init__(parent, style=wx.SIMPLE_BORDER, size=(300, 1080))
        self.SetupScrolling()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.users = []
        self.align_right = align_right

        self.SetSizer(self.sizer)

    def add_user(self, username, status, picture_path):
        user_box = UserBox(self, username, status, picture_path, self.align_right)
        self.users.append(user_box)
        if self.align_right:
            self.sizer.Add(user_box, 0, wx.ALIGN_RIGHT)
        else:
            self.sizer.Add(user_box, 0, wx.ALIGN_LEFT)

    def remove_user(self, username):
        index = -1
        for i in range(len(self.users)):
            if self.users[i].username == username:
                index = i
                break

        if index != -1:
            self.sizer.Remove(index)


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
        self.username_sizer.Add(self.name_input, 1, wx.ALIGN_CENTER)
        self.username_sizer.Add(self.name_submit_button, 1, wx.ALIGN_CENTER)

        self.picture_label = wx.StaticText(self, label='Change profile picture:')
        self.file_picker = wx.FilePickerCtrl(self, style=wx.FLP_OPEN, wildcard="Image files (*.jpg, *.png, "
                                                                               "*.gif)|*.jpg;*.png;*.gif")
        self.pic_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.picture_sizer.Add(self.picture_label, 1, wx.ALIGN_CENTER)
        self.picture_sizer.Add(self.file_picker, 1, wx.ALIGN_CENTER)
        self.picture_sizer.Add(self.pic_submit_button, 1, wx.ALIGN_CENTER)

        self.status_label = wx.StaticText(self, label='Change status:')
        self.status_input = wx.TextCtrl(self, style=wx.TE_LEFT, size=(100, 20))
        self.status_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.status_sizer.Add(self.status_label, 1, wx.ALIGN_CENTER)
        self.status_sizer.Add(self.status_input, 1, wx.ALIGN_CENTER)
        self.status_sizer.Add(self.status_submit_button, 1, wx.ALIGN_CENTER)

        self.password_label = wx.StaticText(self, label='Change password:')
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_LEFT, size=(100, 20))
        self.pass_submit_button = wx.Button(self, label='submit', size=(50, 20))
        self.password_sizer.Add(self.password_label, 1, wx.ALIGN_CENTER)
        self.password_sizer.Add(self.password_input, 1, wx.ALIGN_CENTER)
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
    def __init__(self, parent, username, picture='robot.png'):
        super(CallUserPanel, self).__init__(parent)
        self.username = username
        self.picture = wx.Image(picture, wx.BITMAP_TYPE_ANY)
        self.RELATIVE_SIZE = 0.2

        # Convert the image to bitmap
        scaled_image = self.picture.Rescale(parent.GetSize()[0]*self.RELATIVE_SIZE,
                                            parent.GetSize()[0]*self.RELATIVE_SIZE)
        bitmap = wx.Bitmap(scaled_image)
        # Convert the bitmap to a static bitmap
        self.static_bitmap = wx.StaticBitmap(self, bitmap=bitmap)

        # Text
        self.label = wx.StaticText(self, label=username)
        # Set the font, size and color of the label
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(label_font)
        #self.label.SetForegroundColour(self.TEXT_COLOR)


class CallGrid(wx.GridSizer):
    def __init__(self, parent):
        self.GAP = 3
        self.BORDER_WIDTH = 10

        super(CallGrid, self).__init__(MAX_PARTICIPANTS/2, MAX_PARTICIPANTS/2, self.GAP)
        self.users = []
        self.parent = parent

    def add_user(self, username, picture=None):
        if picture:
            self.users.append(CallUserPanel(self.parent, username, picture))
        else:
            self.users.append(CallUserPanel(self.parent, username))

        self.Add(self.users[-1], 0, wx.EXPAND, self.BORDER_WIDTH)

    def remove_user(self, username):
        for user in self.users:
            if user.username == username:
                self.users.remove(user)
                break


class VoiceCallWindow(wx.Frame):
    def __init__(self, parent, title):
        super(VoiceCallWindow, self).__init__(parent, name=title)
        self.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MINIMIZE_BOX
                                ^ wx.MAXIMIZE_BOX ^ wx.SYSTEM_MENU ^ wx.CLOSE_BOX)

        self.MUTE_BUTTON_IMAGE = wx.Image("mute.png", wx.BITMAP_TYPE_ANY)
        self.LEAVE_BUTTON_IMAGE = wx.Image("leave.png", wx.BITMAP_TYPE_ANY)

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

        self.toolbar.Add(self.mute_button, 1, wx.ALIGN_CENTER)
        self.toolbar.Add(self.leave_call_button, 1, wx.ALIGN_CENTER)

        self.sizer.Add(self.call_grid, 3, wx.ALIGN_CENTER)
        self.sizer.Add(self.toolbar, 1, wx.ALIGN_CENTER)

        self.SetSizer(self.sizer)

    def onMuteToggle(self, event):
        # TODO: handle mute, change icon
        pass

    def onHangup(self, event):
        # TODO: handle logic stuff
        self.Close()

        









