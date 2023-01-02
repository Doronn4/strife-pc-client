import wx


class SignInFrame(wx.Frame):
    def __init__(self, parent, title):
        super(SignInFrame, self).__init__(parent, title=title)

        # Load the background image and set it as the frame's background
        self.background_image = wx.Image("background.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, self.background_image, (0, 0))

        # Create a panel to hold the widgets
        panel = wx.Panel(self)

        # Create the widgets
        self.username_label = wx.StaticText(panel, label="Username:")
        self.password_label = wx.StaticText(panel, label="Password:")
        self.username_input = wx.TextCtrl(panel)
        self.password_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.sign_in_button = wx.Button(panel, label="Sign In")
        self.cancel_button = wx.Button(panel, label="Cancel")

        # Add the widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.username_label, 0, wx.ALL, 5)
        sizer.Add(self.username_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.password_label, 0, wx.ALL, 5)
        sizer.Add(self.password_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.sign_in_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.cancel_button, 0, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

        # Bind the buttons to event handlers
        self.sign_in_button.Bind(wx.EVT_BUTTON, self.on_sign_in)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.SetSize(1280, 720)

    def on_sign_in(self, event):
        # Implement the sign-in logic here
        pass

    def on_cancel(self, event):
        # Close the frame
        self.Close()


if __name__ == '__main__':
    app = wx.App()
    frame = SignInFrame(None, "Sign In")
    frame.Show()
    app.MainLoop()