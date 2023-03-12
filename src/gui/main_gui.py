import wx
import gui_util


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        self.STRIFE_LOGO_IMAGE = wx.Image("assets/strife_logo.png", wx.BITMAP_TYPE_ANY)
        self.VOICE_BUTTON_IMAGE = wx.Image("assets/voice.png", wx.BITMAP_TYPE_ANY)
        self.VIDEO_BUTTON_IMAGE = wx.Image("assets/video.png", wx.BITMAP_TYPE_ANY)
        self.LOGOUT_BUTTON_IMAGE = wx.Image("assets/logout.png", wx.BITMAP_TYPE_ANY)
        self.SETTINGS_BUTTON_IMAGE = wx.Image("assets/settings.png", wx.BITMAP_TYPE_ANY)

        self.RELATIVE_BUTTON_SIZE = 0.04
        self.RELATIVE_SIZE = 0.75  # The relative size of the window to the screen
        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE, wx.DisplaySize()[1] * self.RELATIVE_SIZE

        super(MainFrame, self).__init__(parent, title=title, size=size)

        self.SetIcon(wx.Icon("assets/strife_logo_round.ico", wx.BITMAP_TYPE_ICO))

        # Sub windows
        self.settings_window = gui_util.SettingsDialog(self)
        self.voice_call_window = None  # temp ******
        self.video_call_window = None   # temp ******
        # TODO: Add all the windows....

        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.top_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # My user profile box
        self.my_user_box = gui_util.UserBox(self, gui_util.User())

        # Voice call button
        image_bitmap = self.VOICE_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.voice_call_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # TODO: put a label or id for the button
        # Bind the voice call button to it's function
        self.voice_call_button.Bind(wx.EVT_BUTTON, self.onVoice)

        # Video call button
        image_bitmap = self.VIDEO_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.video_call_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # TODO: put a label or id for the button
        # Bind the video call button to it's function
        self.video_call_button.Bind(wx.EVT_BUTTON, self.onVideo)

        # Logout button
        image_bitmap = self.LOGOUT_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.logout_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # TODO: put a label or id for the button
        # TODO: bind to a function

        # Settings button
        image_bitmap = self.SETTINGS_BUTTON_IMAGE.Scale(
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE,
            wx.DisplaySize()[0] * self.RELATIVE_SIZE * self.RELATIVE_BUTTON_SIZE).ConvertToBitmap()
        self.settings_button = wx.BitmapButton(self, bitmap=image_bitmap)
        # TODO: put a label or id for the button
        # Bind the settings button to it's function
        self.settings_button.Bind(wx.EVT_BUTTON, self.onSettings)

        # Add all the widgets in the top bar to the sizer
        self.top_bar_sizer.Add(self.my_user_box, 3, wx.EXPAND)
        self.top_bar_sizer.Add(self.voice_call_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.video_call_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.logout_button, 1, wx.EXPAND)
        self.top_bar_sizer.Add(self.settings_button, 2, wx.EXPAND)

        self.frame_sizer.Add(self.top_bar_sizer, 1, wx.EXPAND)

        # Sizer of the bottom widgets
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Widgets
        self.friends_panel = gui_util.UsersScrollPanel(self, on_click=self.onChatSelect)
        self.groups_panel = gui_util.GroupsPanel(self)

        # Add all widgets to the sizer
        self.bottom_sizer.Add(self.friends_panel, 1, wx.EXPAND)
        self.bottom_sizer.Add(self.groups_panel, 4, wx.EXPAND)

        # Add bottom sizer to the frame sizer
        self.frame_sizer.Add(self.bottom_sizer, 5, wx.ALIGN_LEFT)

        self.SetSizer(self.frame_sizer)

    def onChatSelect(self, chat_id):
        print('selected chat', chat_id)
        self.groups_panel.sizer.Show(chat_id)

    def onSettings(self, event):
        if not self.settings_window.IsShown():
            self.settings_window = gui_util.SettingsDialog(self)
            self.settings_window.Show()

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


