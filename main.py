#!/usr/bin/env python3
# coding: utf-8

import wx
import os

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="FreeDLHelper", size=(800, 500))

        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    MyFrame()
    app.MainLoop()
