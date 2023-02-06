import wx
import cv2

vs = cv2.VideoCapture(0)


class ImagePanel(wx.Panel):

    def __init__(self, parent, fps=30):
        super().__init__(parent)

        ret, frame = vs.read()
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000. / fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = vs.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='User Capture')
        self.vs = vs
        ImagePanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()