import os
from pathlib import Path
import ctypes
import wx
from login_gui import LoginFrame
from main_gui import MainFrame
from gui_util import User


if __name__ == '__main__':
    script_path = Path(os.path.abspath(__file__))
    wd = script_path.parent.parent.parent
    os.chdir(str(wd))

    app = wx.App()
    main_frame = MainFrame(parent=None, title='Strife')
    main_frame.Show()


    # # For testing
    # main_frame.friends_panel.add_user(User(f'iftah fans', '', 'assets/robot.png', chat_id=69))
    # main_frame.friends_panel.add_user(User(f'da boys', '', 'assets/robot.png', chat_id=420))
    #
    # itamar = User(f'itamar', 'sup', 'assets/robot.png')
    # gabzo = User(f'gabzo', 'hello there', 'assets/robot.png')
    #
    # main_frame.groups_panel.sizer.add_group(69, [itamar, itamar, itamar])
    # main_frame.groups_panel.sizer.add_group(420, [gabzo, gabzo])
    #
    # for i in range(20):
    #     main_frame.groups_panel.sizer.groups[69][0].add_text_message(itamar, 'hello everyone!'+str(i))

    app.MainLoop()


