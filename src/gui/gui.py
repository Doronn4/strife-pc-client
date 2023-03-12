import os
from pathlib import Path
import ctypes
import wx
from login_gui import LoginFrame
from main_gui import MainFrame
from gui_util import LoginEvent, EVT_LOGIN_BINDER
from gui_util import User
import wx.lib.inspection as inspect


class StrifeApp(wx.App):
    login_frame: LoginFrame
    main_frame: MainFrame

    def OnInit(self):
        my_app_id = r'doron.strife.pc.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

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
    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))

    app = StrifeApp()
    # For testing
    app.main_frame.friends_panel.add_user(User(f'iftah fans', '', 'assets/robot.png', chat_id=69))
    app.main_frame.friends_panel.add_user(User(f'da boys', '', 'assets/robot.png', chat_id=420))

    itamar = User(f'itamar', 'sup', 'assets/robot.png')
    gabzo = User(f'gabzo', 'hello there', 'assets/robot.png')

    app.main_frame.groups_panel.sizer.add_group(69, [itamar, itamar, itamar])
    app.main_frame.groups_panel.sizer.add_group(420, [gabzo, gabzo])

    for i in range(20):
        app.main_frame.groups_panel.sizer.groups[69][0].add_text_message(itamar, 'hello everyone!'+str(i))

    inspect.InspectionTool().Show()

    app.MainLoop()


