#!/usr/bin/env python3
# coding: utf-8

import wx
import os
import audiofile
import scinfo


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="FreeDLHelper", size=(900, 550))

        # ** ステータスバー **
        self.CreateStatusBar()
        self.SetStatusText('音声ファイルをドラッグ&ドロップしてください')
        self.GetStatusBar().SetBackgroundColour(None)

        # ** 構築 **
        root_panel = wx.Panel(self)

        # アートワーク
        aw_panel = ArtworkPanel(root_panel, imgsize=(300, 300))
        # ファイルパス
        fr_panel = FileRefPanel(root_panel)
        # 曲情報
        ai_panel = AudioInfoPanel(root_panel)
        # URL入力欄
        url_panel = URLTextPanel(root_panel)
        # ボタン
        bt_panel = ButtonPanel(root_panel)

        root_layout = wx.GridBagSizer()
        root_layout.Add(aw_panel, (0, 0), (2, 1), flag=wx.ALL, border=10)
        root_layout.Add(fr_panel, (0, 1), (1, 1), flag=wx.EXPAND | wx.ALL, border=10)
        root_layout.Add(ai_panel, (1, 1), (1, 1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        root_layout.Add(url_panel, (2, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        root_layout.Add(bt_panel, (3, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        root_layout.AddGrowableCol(1)

        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

        self.Show()
        self.Center()  # 画面中央に表示


class FileRefPanel(wx.Panel):
    """ ファイルパス入力部分 """
    
    def __init__(self, parent):
        super().__init__(parent)

        s_box = wx.StaticBox(self, -1, 'ファイル')

        # ** 各項目 **
        self.tc_file = wx.TextCtrl(self, -1)
        bt_file = wx.Button(self, -1, label='ファイル選択')

        # イベント設定: ダイアログ表示
        bt_file.Bind(wx.EVT_BUTTON, self.click_bt_file)

        # 配置
        grid = wx.FlexGridSizer(cols=2, gap=(0, 0))
        grid.Add(self.tc_file, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(bt_file, flag=wx.ALL, border=10)

        # 引き伸ばし
        grid.AddGrowableCol(0)

        layout = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        layout.Add(grid, 1)
        self.SetSizer(layout)
    
    def click_bt_file(self, event):
        """
        ダイアログ表示・パス取得イベント
        """
        # ダイアログ設定
        dialog = wx.FileDialog(self, 'ファイルを選択してください')

        # ファイルが選択された場合
        if dialog.ShowModal() == wx.ID_OK:
            # パスを取得
            filepath = dialog.GetPath()
            # テキストボックスにパス設定
            self.tc_file.SetValue(filepath)
        
        # ダイアログを破棄
        dialog.Destroy()


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
        newimg = img.Scale(
            self.imgsize[0], self.imgsize[1], wx.IMAGE_QUALITY_HIGH)
        # 画像描画部
        img_panel = wx.StaticBitmap(self, -1, wx.Bitmap(newimg))
        # タイトル付きBoxSizer
        box = wx.StaticBox(self, -1, 'アートワーク')
        # 構築
        layout = wx.StaticBoxSizer(box, wx.VERTICAL)
        layout.Add(img_panel)
        self.SetSizer(layout)


class AudioInfoPanel(wx.Panel):
    """ 曲情報パネル """

    def __init__(self, parent):
        super().__init__(parent)
        # ** 各項目 **
        st_title = wx.StaticText(self, -1, 'タイトル: ')
        tc_title = wx.TextCtrl(self, -1)

        st_album = wx.StaticText(self, -1, 'アルバム名: ')
        tc_album = wx.TextCtrl(self, -1)

        st_artist = wx.StaticText(self, -1, 'アーティスト名: ')
        tc_artist = wx.TextCtrl(self, -1)

        st_genre = wx.StaticText(self, -1, 'ジャンル: ')
        tc_genre = wx.ComboBox(self, -1, '選択してください', choices=[], style=wx.CB_DROPDOWN)

        # タイトル付きBoxSizer
        s_box = wx.StaticBox(self, -1, '曲情報')

        # 配置
        grid = wx.FlexGridSizer(cols=2, gap=(0,0))
        grid.Add(st_title, flag=wx.ALL, border=10)
        grid.Add(tc_title, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_album, flag=wx.ALL, border=10)
        grid.Add(tc_album, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_artist, flag=wx.ALL, border=10)
        grid.Add(tc_artist, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_genre, flag=wx.ALL, border=10)
        grid.Add(tc_genre, flag=wx.EXPAND | wx.ALL, border=10)

        # 引き伸ばし
        grid.AddGrowableCol(1)

        # 構築
        layout = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        layout.Add(grid, 1)
        self.SetSizer(layout)


class URLTextPanel(wx.Panel):
    """ URL入力パネル """

    def __init__(self, parent):
        super().__init__(parent)

        s_box = wx.StaticBox(self, -1, 'SoundCloudのURL')

        # ** 各項目 **
        tc_url = wx.TextCtrl(self, -1)

        # 配置
        grid = wx.FlexGridSizer(cols=1, gap=(0, 0))
        grid.Add(tc_url, flag=wx.EXPAND | wx.ALL, border=10)

        # 引き伸ばし
        grid.AddGrowableCol(0)

        layout = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        layout.Add(grid, 1)
        self.SetSizer(layout)


class ButtonPanel(wx.Panel):
    """ ボタン用 """

    def __init__(self, parent):
        super().__init__(parent)
        
        # ** 各項目 **
        bt_get = wx.Button(self, -1, label='情報取得')
        bt_edit = wx.Button(self, -1, label='書き込み')

        # 配置
        grid = wx.FlexGridSizer(cols=2, gap=(0, 0))
        grid.Add(bt_get, flag=wx.LEFT, border=200)
        grid.Add(bt_edit, flag=wx.RIGHT, border=200)
        grid.AddGrowableCol(0)

        self.SetSizer(grid)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
