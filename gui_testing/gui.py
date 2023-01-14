import wx
from login_gui import LoginFrame
from main_gui import MainFrame


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        # hbox = wx.BoxSizer(wx.HORIZONTAL)


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        self.RELATIVE_SIZE = 0.75  # The relative size of the window to the screen
        size = wx.DisplaySize()[0] * self.RELATIVE_SIZE, wx.DisplaySize()[1] * self.RELATIVE_SIZE

        super(MyFrame, self).__init__(parent, title=title)

        self.panel = MyPanel(self)


class StrifeApp(wx.App):
    login_frame: LoginFrame
    main_frame: MainFrame

    def OnInit(self):
        #self.login_frame = LoginFrame(parent=None, title='Login to Strife')
        #self.login_frame.Show()
        self.main_frame = MainFrame(parent=None, title='Strife')
        self.main_frame.Show()

        return True


if __name__ == '__main__':
    app = StrifeApp()
    for i in range(20):
        app.main_frame.friends_panel.add_user(f'doron{i}', 'hello world', 'robot.png')
    app.MainLoop()
