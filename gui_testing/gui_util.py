import wx
from wx.lib.scrolledpanel import ScrolledPanel


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
    def __init__(self, parent, username='', status='', pic='strife_logo.png'):
        super(UserBox, self).__init__(wx.HORIZONTAL)
        self.RELATIVE_PIC_SIZE = 0.04

        self.parent = parent
        self.username = username
        self.status = status
        self.pic = pic

        # Add user profile picture
        pic = wx.Image(self.pic, wx.BITMAP_TYPE_ANY)\
            .Scale(wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE, wx.DisplaySize()[0] * self.RELATIVE_PIC_SIZE)
        bitmap = wx.Bitmap(pic)
        static_pic = wx.StaticBitmap(self.parent, bitmap=bitmap)
        self.Add(static_pic, 0, wx.ALIGN_CENTER)

        # Add vertical sizer that contains the username and status
        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # Add the username to it
        username_text = wx.StaticText(self.parent, label=self.username)
        self.vsizer.Add(username_text, 1, wx.EXPAND)

        # Add the status
        status_text = wx.StaticText(self.parent, label=self.status)
        self.vsizer.Add(status_text, 1, wx.EXPAND)

        # Add the vertical sizer to the sizer
        self.Add(self.vsizer, 0, wx.ALIGN_CENTER)


class UsersScrollPanel(ScrolledPanel):
    def __init__(self, parent):
        super(UsersScrollPanel, self).__init__(parent, style=wx.SIMPLE_BORDER, size=(300, 1080))
        self.SetupScrolling()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.users = []

        self.SetSizer(self.sizer)

    def add_user(self, username, status, picture_path):
        user_box = UserBox(self, username, status, picture_path)
        self.users.append(user_box)
        self.sizer.Add(user_box)

    def remove_user(self, username):
        index = -1
        for i in range(len(self.users)):
            if self.users[i].username == username:
                index = i
                break

        if index != -1:
            self.sizer.Remove(index)