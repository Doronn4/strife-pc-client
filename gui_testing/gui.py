import wx
from login_gui import LoginFrame
from main_gui import MainFrame
from gui_util import LoginEvent, EVT_LOGIN_BINDER


class StrifeApp(wx.App):
    login_frame: LoginFrame
    main_frame: MainFrame

    def OnInit(self):
        self.login_frame = LoginFrame(parent=None, title='Login to Strife', app=self)
        self.Bind(EVT_LOGIN_BINDER, self.onLoginAttempt)
        self.login_frame.Show()
        self.main_frame = MainFrame(parent=None, title='Strife')

        return True

    def onLoginAttempt(self, event):
        print(event)
        username, password = event.username, event.password
        print('login attempt with', username, password)
        # Add logic
        self.login_frame.Close()
        self.main_frame.Show()


if __name__ == '__main__':
    app = StrifeApp()
    # For testing
    for i in range(20):
        app.main_frame.friends_panel.add_user(f'DORON{i}', 'hello world', 'graphics/robot.png')

    for i in range(6):
        app.main_frame.chat_members_panel.add_user(f'itamar{i}', 'sup', 'graphics/robot.png')

    app.MainLoop()


