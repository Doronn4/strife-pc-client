import wx
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QLabel


class EmbeddedQtPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.qapp = QApplication([])
        self.qlabel = QLabel()
        self.qapp.setActiveWindow(self.qlabel)

    def SetFocus(self):
        self.qlabel.setFocus()

    def GetHandle(self):
        return self.qlabel.winId()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None)
        self.embedded_panel = EmbeddedQtPanel(self)
        print(type(self.embedded_panel.GetHandle()))
        self.embedded_panel.qlabel.setParent(self.embedded_panel.GetHandle())


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()



