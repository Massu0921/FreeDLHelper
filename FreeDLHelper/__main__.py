# Pyinstaller用に絶対パスで指定
import wx
from FreeDLHelper.myframe import MyFrame

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
