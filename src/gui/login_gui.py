import os

import wx
from gui_util import PanelsSwitcher, LoginEvent, EVT_LOGIN_BINDER, EVT_LOGIN


class RegisterPanel(wx.Panel):
    """
    The register panel (Used for registering to the Strife system)
    """
    def __init__(self, parent, onRegister, toLogin):
        """
        Creates a new register panel
        :param parent: The parent of the panel
        :param onRegister: The function to call when the user pressed the 'register' button
        :param toLogin: The function to move to the login window (panel)
        """
        # The function to move to the login window (panel)
        self.toLogin = toLogin
        # The function to call when the user pressed the 'register' button
        self.onRegister = onRegister
        # The relative size of the window to the screen
        self.RELATIVE_SIZE = 0.5
        # The background color of the panel
        self.BACKGROUND_COLOR = wx.Colour(0, 53, 69)
        # A default text color
        self.TEXT_COLOR = wx.Colour(237, 99, 99)
        # The strife logo image
        self.STRIFE_IMAGE = wx.Image("assets/strife_logo.png", wx.BITMAP_TYPE_ANY)
        # The relative size of the image compared to the size of the window
        self.RELATIVE_LOGO_SIZE = 0.15

        # Calculate the size of the window
        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE * 0.75, wx.DisplaySize()[1] * self.RELATIVE_SIZE
        # Call to super init method
        super(RegisterPanel, self).__init__(parent, size=size)
        # Set background color
        self.SetBackgroundColour(self.BACKGROUND_COLOR)
        # Create the sizer of the panel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Label for moving to the login screen

        # The font of the label
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # Register label
        register_label = wx.StaticText(self, label="Already have an account? Login")
        # Change the font
        register_label.SetFont(label_font)
        # Change the color
        register_label.SetForegroundColour(self.TEXT_COLOR)
        # Bind label to function
        register_label.Bind(wx.EVT_LEFT_DOWN, self.toLogin)
        # Add label to sizer
        self.sizer.Add(register_label, 0, wx.ALIGN_RIGHT)

        # Add space between the widgets in the spacer
        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.01)

        # Get the ratio of the logo
        ratio = self.STRIFE_IMAGE.GetHeight() / self.STRIFE_IMAGE.GetWidth()
        # Calculate the new width
        new_width = wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_LOGO_SIZE
        # Rescale the logo image
        scaled_image = self.STRIFE_IMAGE.Rescale(new_width, ratio * new_width)
        # Convert the image to bitmap
        bitmap = wx.Bitmap(scaled_image)
        # Convert the bitmap to a static bitmap
        static_bitmap = wx.StaticBitmap(self, bitmap=bitmap)
        # Adding the strife logo image to the sizer
        self.sizer.Add(static_bitmap, 0, wx.ALIGN_CENTER)

        # Add space between the widgets in the spacer
        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.05)

        # Text
        self.label = wx.StaticText(self, label='STRIFE REGISTER')
        # Set the font, size and color of the label
        label_font = wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(label_font)
        self.label.SetForegroundColour(self.TEXT_COLOR)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER)

        # Add space between the widgets in the spacer
        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.1)

        # Font used for the username and password fields
        label_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Username input field
        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Enter username label
        username_label = wx.StaticText(self, label='Choose username: ')
        # Change the font
        username_label.SetFont(label_font)
        # Add the label to the username sizer
        username_sizer.Add(username_label, 0, wx.ALIGN_CENTER)
        # Add the input to the username sizer
        self.username_input = wx.TextCtrl(self, style=wx.TE_CENTER, size=(200, 30))
        username_sizer.Add(self.username_input, 0, wx.ALIGN_CENTER)
        # Change the font
        self.username_input.SetFont(label_font)
        # Add the username sizer to the frame sizer
        self.sizer.Add(username_sizer, 0, wx.ALIGN_CENTER)

        # Add space between the widgets in the spacer
        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.01)

        # Password input field
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Enter password label
        password_label = wx.StaticText(self, label='Choose password: ')
        # Change the font
        password_label.SetFont(label_font)
        # Add the label to the password sizer
        password_sizer.Add(password_label, 0, wx.ALIGN_CENTER)
        # Add the input to the password sizer
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_CENTER, size=(200, 30))
        password_sizer.Add(self.password_input, 0, wx.ALIGN_CENTER)
        # Change the font
        self.password_input.SetFont(label_font)
        # Add the password sizer to the frame sizer
        self.sizer.Add(password_sizer, 0, wx.ALIGN_CENTER)

        # Add space between the widgets in the spacer
        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.04)

        # Submit button
        button_label = 'Register'
        self.submit_button = wx.Button(self, label=button_label, size=(120, 30))
        self.submit_button.Bind(wx.EVT_BUTTON, self.onRegister)
        self.sizer.Add(self.submit_button, 0, wx.ALIGN_CENTER)

        # Set the sizer of the window
        self.SetSizer(self.sizer)


class LoginPanel(wx.Panel):
    """
    The login panel (Used for logging in to the Strife system)
    """
    def __init__(self, parent, onLogin, toRegister):
        self.toRegister = toRegister
        self.onLogin = onLogin
        self.RELATIVE_SIZE = 0.5  # The relative size of the window to the screen
        self.BACKGROUND_COLOR = wx.Colour(0, 53, 69)
        self.TEXT_COLOR = wx.Colour(237, 99, 99)
        self.STRIFE_IMAGE = wx.Image("assets/strife_logo.png", wx.BITMAP_TYPE_ANY)
        self.RELATIVE_LOGO_SIZE = 0.15  # The size of the logo relative to the size of the window

        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE * 0.75, wx.DisplaySize()[1] * self.RELATIVE_SIZE

        super(LoginPanel, self).__init__(parent, size=size)

        self.SetBackgroundColour(self.BACKGROUND_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # Register label
        register_label = wx.StaticText(self, label="Don't have an account? Register")
        # Change the font
        register_label.SetFont(label_font)
        # Change the color
        register_label.SetForegroundColour(self.TEXT_COLOR)
        # Bind label to function
        register_label.Bind(wx.EVT_LEFT_DOWN, self.toRegister)
        # Add label to sizer
        self.sizer.Add(register_label, 0, wx.ALIGN_RIGHT)

        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.01)

        # Get the ratio of the logo
        ratio = self.STRIFE_IMAGE.GetHeight() / self.STRIFE_IMAGE.GetWidth()
        # Calculate the new width
        new_width = wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_LOGO_SIZE
        # Rescale the logo image
        scaled_image = self.STRIFE_IMAGE.Rescale(new_width, ratio * new_width)
        # Convert the image to bitmap
        bitmap = wx.Bitmap(scaled_image)
        # Convert the bitmap to a static bitmap
        static_bitmap = wx.StaticBitmap(self, bitmap=bitmap)
        # Adding the strife logo image to the sizer
        self.sizer.Add(static_bitmap, 0, wx.ALIGN_CENTER)

        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.05)

        # Text
        self.label = wx.StaticText(self, label='STRIFE LOGIN')
        # Set the font, size and color of the label
        label_font = wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(label_font)
        self.label.SetForegroundColour(self.TEXT_COLOR)
        self.sizer.Add(self.label, 0, wx.ALIGN_CENTER)

        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.1)

        # Font used for the username and password fields
        label_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Username input field
        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Enter username label
        username_label = wx.StaticText(self, label='Enter username: ')
        # Change the font
        username_label.SetFont(label_font)
        # Add the label to the username sizer
        username_sizer.Add(username_label, 0, wx.ALIGN_CENTER)
        # Add the input to the username sizer
        self.username_input = wx.TextCtrl(self, style=wx.TE_CENTER, size=(200,30))
        username_sizer.Add(self.username_input, 0, wx.ALIGN_CENTER)
        # Change the font
        self.username_input.SetFont(label_font)
        # Add the username sizer to the frame sizer
        self.sizer.Add(username_sizer, 0, wx.ALIGN_CENTER)

        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.01)

        # Password input field
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Enter password label
        password_label = wx.StaticText(self, label='Enter password: ')
        # Change the font
        password_label.SetFont(label_font)
        # Add the label to the password sizer
        password_sizer.Add(password_label, 0, wx.ALIGN_CENTER)
        # Add the input to the password sizer
        self.password_input = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_CENTER, size=(200,30))
        password_sizer.Add(self.password_input, 0, wx.ALIGN_CENTER)
        # Change the font
        self.password_input.SetFont(label_font)
        # Add the password sizer to the frame sizer
        self.sizer.Add(password_sizer, 0, wx.ALIGN_CENTER)

        self.sizer.AddSpacer(wx.DisplaySize()[1] * self.RELATIVE_SIZE * 0.04)

        # Submit button
        button_label = 'Log In'
        self.submit_button = wx.Button(self, label=button_label, size=(120, 30))
        self.submit_button.Bind(wx.EVT_BUTTON, self.onLogin)
        self.sizer.Add(self.submit_button, 0, wx.ALIGN_CENTER)

        self.SetSizer(self.sizer)


class LoginFrame(wx.Frame):
    """
    The login window for the strife system (Logging in and registering)
    """

    def __init__(self, parent, title, app):
        self.RELATIVE_SIZE = 0.5  # The relative size of the window to the screen
        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE * 0.75, wx.DisplaySize()[1] * self.RELATIVE_SIZE
        super(LoginFrame, self).__init__(parent, title=title, size=size)

        self.SetIcon(wx.Icon("assets/strife_logo_round.ico", wx.BITMAP_TYPE_ICO))

        self.app = app
        self.login_panel = LoginPanel(self, self.onLogin, self.toRegister)
        self.register_panel = RegisterPanel(self, self.onRegister, self.toLogin)

        self.panel_switcher = PanelsSwitcher(self, [self.login_panel, self.register_panel])

    def onLogin(self, event):
        error_str = ''
        # Get the username and password passed by the user
        username = self.login_panel.username_input.GetValue()
        password = self.login_panel.password_input.GetValue()

        # Check if username and password are valid (before sending them)
        error_str = self.check_username(username)
        if error_str:
            # Pop up dialog with the error string
            pass

        else:
            error_str = self.check_password(username)
            if error_str:
                # Pop up dialog with the error string
                pass

        # Pass the username and password to the main program...
        if not error_str:
            login_event = LoginEvent(EVT_LOGIN, self.GetId())
            login_event.set_credentials(username, password)
            # Send the event
            wx.PostEvent(self.app, login_event)

    def toRegister(self, event):
        self.panel_switcher.Show(self.register_panel)

    def onRegister(self, event):
        pass

    def toLogin(self, event):
        self.panel_switcher.Show(self.login_panel)

    def check_password(self, password: str) -> str:
        pass

    def check_username(self, username: str) -> str:
        pass
