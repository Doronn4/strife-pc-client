import threading

import wx
import cv2
import numpy as np


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Video Frame')
        self.panel = wx.Panel(self)
        self.bmp = wx.Bitmap(640, 480)
        self.static_bmp = wx.StaticBitmap(self.panel, -1, self.bmp)
        self.Show()
        threading.Thread(target=self.run).start()

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.bmp.CopyFromBuffer(frame)
        self.static_bmp.SetBitmap(self.bmp)
        self.Refresh()

    def run(self):
        # Your code to receive video frames and decode them
        while True:
            frame = receive_frame()
            print(frame)
            self.update_frame(frame)


def receive_frame():
    return cam.read()[1]


if __name__ == '__main__':
    cam = cv2.VideoCapture(0)
    app = wx.App(redirect=False)
    frame = MyFrame()
    app.MainLoop()
