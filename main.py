#!/usr/bin/env python3
# coding: utf-8

import wx
import os
import audiofile
import scinfo

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="FreeDLHelper", size=(800, 500))

        # ** ステータスバー **
        self.CreateStatusBar()
        self.SetStatusText('音声ファイルをドラッグ&ドロップしてください')
        self.GetStatusBar().SetBackgroundColour(None)

        # ** 構築 **
        root_panel = wx.Panel(self)

        # アートワーク
        aw_panel = ArtworkPanel(root_panel, imgsize=(300,300))
        
        root_layout = wx.BoxSizer(wx.VERTICAL)
        root_layout.Add(aw_panel, 0, wx.ALL, 10)

        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

        self.Show()
        self.Center()  # 画面中央に表示

class ArtworkPanel(wx.Panel):
    """ アートワーク画像表示部分 """
    def __init__(self, parent, imgsize):
        super().__init__(parent)
        self.imgsize = imgsize
        self.set_img()

    def set_img(self, input_image=''):
        """ 画像設定用 """

        if input_image == '':
            image = 'dnd_file.jpg'
        else:
            image = input_image

        img = wx.Image(image)
        # サイズ・品質
        newimg = img.Scale(self.imgsize[0], self.imgsize[1], wx.IMAGE_QUALITY_HIGH)
        # 画像描画部
        img_panel = wx.StaticBitmap(self, -1, wx.Bitmap(newimg))
        # タイトル付きBoxSizer
        box = wx.StaticBox(self, -1, 'アートワーク')
        # 構成
        layout = wx.StaticBoxSizer(box, wx.VERTICAL)
        layout.Add(img_panel)
        self.SetSizer(layout)

class URLTextPanel(wx.Panel):
    """ URL入力用のテキストボックス """
    def __init__(self, parent):
        pass

class AudioInfoPanel(wx.Panel):
    """ 曲情報テキストボックス """
    def __init__(self, parent):
        pass

class ButtonPanel(wx.Panel):
    """ ボタン用 """
    def __init__(self, parent):
        pass

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
