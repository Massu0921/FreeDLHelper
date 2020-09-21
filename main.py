#!/usr/bin/env python3
# coding: utf-8

import wx
import os
import sys
import io
import pyperclip
import audiofile
import scinfo
from urllib.request import urlopen

# リソースアクセス用
def ResourcePath(filename):
  if hasattr(sys, "_MEIPASS"):
      return os.path.join(sys._MEIPASS, filename)
  return os.path.join(filename)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="FreeDLHelper v1.3", size=(900, 550))

        # ** ステータスバー **
        self.CreateStatusBar()
        self.SetStatusText('音声ファイルをドラッグ&ドロップしてください')
        self.GetStatusBar().SetBackgroundColour(None)

        # ** アイコン **
        #tbi = wx.adv.TaskBarIcon()
        icon = wx.Icon(ResourcePath('Resources/fdh_v2.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # scinfo, audiofileのインスタンス作成
        sc = scinfo.SoundCloudInfo()
        af = audiofile.AudioFile()

        # ** 構築 ** sc, afは参照渡し
        root_panel = wx.Panel(self)

        # 曲情報
        self.ai_panel = AudioInfoPanel(root_panel)
        # アートワーク
        self.aw_panel = ArtworkPanel(root_panel, imgsize=(300, 300))
        # URL入力欄
        self.url_panel = URLTextPanel(root_panel)
        # ファイルパス
        self.fr_panel = FileRefPanel(root_panel, sc, af)
        # ボタン
        self.bt_panel = ButtonPanel(root_panel, sc, af)

        root_layout = wx.GridBagSizer()
        root_layout.Add(self.aw_panel, (0, 0), (2, 1), flag=wx.ALL, border=10)
        root_layout.Add(self.fr_panel, (0, 1), (1, 1), flag=wx.EXPAND | wx.ALL, border=10)
        root_layout.Add(self.ai_panel, (1, 1), (1, 1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        root_layout.Add(self.url_panel, (2, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        root_layout.Add(self.bt_panel, (3, 0), (1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        root_layout.AddGrowableCol(1)

        root_panel.SetSizer(root_layout)
        root_layout.Fit(root_panel)

        # ドラッグ&ドロップの設定
        fdt = MyFileDropTarget(root_panel, sc, af)
        root_panel.SetDropTarget(fdt)

        self.Show()
        self.Center()  # 画面中央に表示


class FileRefPanel(wx.Panel):
    """ ファイルパス入力部分 """

    def __init__(self, parent, sc, af):
        super().__init__(parent)

        # scinfo, audiofileのインスタンス(参照)
        self.sc = sc
        self.af = af

        # AudioInfoPanel内のテキストボックス
        self.cb_title = parent.GetParent().ai_panel.cb_title
        self.cb_album = parent.GetParent().ai_panel.cb_album
        self.cb_artist = parent.GetParent().ai_panel.cb_artist
        self.cb_genre = parent.GetParent().ai_panel.cb_genre
        self.tc_comment = parent.GetParent().ai_panel.tc_comment

        # URL入力欄
        self.tc_url = parent.GetParent().url_panel.tc_url

        # ArtworkPanelの画像設定メソッド
        self.set_img = parent.GetParent().aw_panel.set_img

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

        # 曲情報のドロップダウンリストを初期化
        titlelist = ['']
        albumlist = ['']
        artistlist = ['']
        genrelist = ['']

        # ダイアログ設定
        file_filter = \
            "audio file(*.wav;*.aif;*.aiff;*.aifc;*.afc;*.flac;*.fla;*.mp3;*.m4a) \
            | *.aif;*.aiff;*.aifc;*.afc;*.flac;*.fla;*.mp3;*.m4a; \
            | all file(*.*) | *.*"
        dialog = wx.FileDialog(self, 'ファイルを選択してください', wildcard=file_filter)

        # ファイルが選択された場合
        if dialog.ShowModal() == wx.ID_OK:

            # アートワークURLを初期化
            self.sc.artwork_url = ''

            # パスを取得
            filepath = dialog.GetPath()

            # ファイル読み込み
            try:
                self.af.info(filepath)

                # アートワークを更新
                self.set_img(self.af.artwork)

                # ジャンルを入力
                genrelist = [self.af.genre]
                self.cb_genre.SetItems(genrelist)
                self.cb_genre.SetValue(self.af.genre)

                self.GetTopLevelParent().SetStatusText(
                    'ファイルの読み込みが完了しました。SoundCloudのURLを入力し、"情報取得"を押してください')

            except audiofile.FileFormatError:
                wx.MessageBox('ファイルが未対応のフォーマットです', '読み込みエラー', wx.ICON_ERROR)

                # アートワークを初期状態に
                self.set_img()

                # ジャンルを初期状態に
                self.cb_genre.SetItems(genrelist)
                self.cb_genre.SetValue('選択してください')

                self.GetTopLevelParent().SetStatusText('読み込みエラーです。ファイルを確認してください')

            # テキストボックスにパス設定
            self.tc_file.SetValue(self.af.filepath)
            
            # ジャンル以外のドロップダウンリストを更新
            titlelist = [self.af.title]
            albumlist = [self.af.album]
            artistlist = [self.af.artist]

            self.cb_title.SetItems(titlelist)
            self.cb_album.SetItems(albumlist)
            self.cb_artist.SetItems(artistlist)

            # 曲情報を入力
            self.cb_title.SetValue(self.af.title)
            self.cb_album.SetValue(self.af.album)
            self.cb_artist.SetValue(self.af.artist)
            self.tc_comment.SetValue(self.af.comment)

            # URL入力欄をクリア
            self.tc_url.Clear()

        # ダイアログを破棄
        dialog.Destroy()


class MyFileDropTarget(wx.FileDropTarget):
    """ ドラッグ&ドロップ """

    def __init__(self, parent, sc, af):
        wx.FileDropTarget.__init__(self)

        self.parent = parent

        # scinfo, audiofileのインスタンス(参照)
        self.sc = sc
        self.af = af

        # AudioInfoPanel内のテキストボックス
        self.cb_title = parent.GetParent().ai_panel.cb_title
        self.cb_album = parent.GetParent().ai_panel.cb_album
        self.cb_artist = parent.GetParent().ai_panel.cb_artist
        self.cb_genre = parent.GetParent().ai_panel.cb_genre
        self.tc_comment = parent.GetParent().ai_panel.tc_comment

        # URL入力欄
        self.tc_url = parent.GetParent().url_panel.tc_url

        # FileRefPanelのテキストボックス
        self.tc_file = parent.GetParent().fr_panel.tc_file

        # ArtworkPanelの画像設定メソッド
        self.set_img = parent.GetParent().aw_panel.set_img

    def OnDropFiles(self, x, y, filenames):

        # 各リストを初期化
        titlelist = ['']
        albumlist = ['']
        artistlist = ['']
        genrelist = ['']

        # アートワークURLを初期化
        self.sc.artwork_url = ''

        # D&Dされたパスを取得
        dnd_filepath = filenames[0]

        # ファイル読み込み
        try:
            self.af.info(dnd_filepath)

            # アートワークを更新
            self.set_img(self.af.artwork)

            # ジャンルを入力
            genrelist = [self.af.genre]
            self.cb_genre.SetItems(genrelist)
            self.cb_genre.SetValue(self.af.genre)

            self.parent.GetTopLevelParent().SetStatusText(
                'ファイルの読み込みが完了しました。SoundCloudのURLを入力し、"情報取得"を押してください')

        except audiofile.FileFormatError:
            wx.MessageBox('ファイルが未対応のフォーマットです', '読み込みエラー', wx.ICON_ERROR)
            self.parent.GetTopLevelParent().SetStatusText('読み込みエラーです。ファイルを確認してください')

        except audiofile.FFmpegNotFoundError:
            wx.MessageBox('ffmpegが見つかりませんでした', '変換エラー', wx.ICON_ERROR)
            self.parent.GetTopLevelParent().SetStatusText('変換エラーです。ffmpegを本アプリと同じディレクトリにインストールしてください')

        except audiofile.JsonLoadError:
            wx.MessageBox('config.jsonの読み込みに失敗しました', '読み込みエラー', wx.ICON_ERROR)
            self.parent.GetTopLevelParent().SetStatusText('読み込みエラーです。config.jsonを確認してください')

        except audiofile.CommandFailedError:
            wx.MessageBox('ffmpegのコマンド実行に失敗しました', '変換エラー', wx.ICON_ERROR)
            self.parent.GetTopLevelParent().SetStatusText('変換エラーです。config.json内の設定を確認してください')

            # アートワークを初期状態に
            self.set_img()

            # ジャンルを初期状態に
            self.cb_genre.SetItems(genrelist)
            self.cb_genre.SetValue('選択してください')

        # テキストボックスにパス設定
        self.tc_file.SetValue(self.af.filepath)

        # ジャンル以外のドロップダウンリストを更新
        titlelist = [self.af.title]
        albumlist = [self.af.album]
        artistlist = [self.af.artist]

        self.cb_title.SetItems(titlelist)
        self.cb_album.SetItems(albumlist)
        self.cb_artist.SetItems(artistlist)

        # 曲情報を入力
        self.cb_title.SetValue(self.af.title)
        self.cb_album.SetValue(self.af.album)
        self.cb_artist.SetValue(self.af.artist)
        self.tc_comment.SetValue(self.af.comment)

        # URL入力欄をクリア
        self.tc_url.Clear()

        return True


class ArtworkPanel(wx.Panel):
    """ アートワーク画像表示部分 """

    def __init__(self, parent, imgsize):
        super().__init__(parent)
        self.imgsize = imgsize

        image = ResourcePath('Resources/dnd_file.jpg')
        img = wx.Image(image)

        # サイズ・品質
        newimg = img.Scale(self.imgsize[0], self.imgsize[1], wx.IMAGE_QUALITY_HIGH)
        self.img_panel = wx.StaticBitmap(self, -1, wx.Bitmap(newimg))

        # タイトル付きBoxSizer
        box = wx.StaticBox(self, -1, 'アートワーク')

        # 構築
        layout = wx.StaticBoxSizer(box, wx.VERTICAL)
        layout.Add(self.img_panel)

        self.SetSizer(layout)

        img.Destroy()

    def set_img(self, img_data=-1):
        """
        画像変更用

        Parameters
        ----------
        img_data : str or bytes or None
            画像のURL(str), bytes型のデータ, ない場合はNone
        """

        # URL(文字列)の場合
        if type(img_data) is str:
            image = urlopen(img_data).read()
            image = io.BytesIO(image)

        # 画像データ(bytes)の場合
        elif type(img_data) is bytes:
            image = io.BytesIO(img_data)

        # 画像がない(None)場合
        elif img_data == None:
            image = ResourcePath('Resources/no_artwork.jpg')

        # 引数なし
        elif img_data == -1:
            image = ResourcePath('Resources/dnd_file.jpg')

        img = wx.Image(image)
        # サイズ・品質
        newimg = img.Scale(self.imgsize[0], self.imgsize[1], wx.IMAGE_QUALITY_HIGH)

        # 画像変更
        self.img_panel.SetBitmap(wx.Bitmap(newimg))

        img.Destroy()


class AudioInfoPanel(wx.Panel):
    """
    曲情報パネル

    Attributes
    ----------
    cb_title : wx.ComboBox
        タイトルのテキストボックス
    cb_album : wx.ComboBox
        アルバム名のテキストボックス
    cb_artist : wx.ComboBox
        アーティスト名のテキストボックス
    cb_genre : wx.ComboBox
        ジャンル一覧
    tc_comment : wx.TextCtrl
        コメントのテキストボックス
    """

    def __init__(self, parent):
        super().__init__(parent)

        # ** 各項目 **
        st_title = wx.StaticText(self, -1, 'タイトル: ')
        self.cb_title = wx.ComboBox(self, -1, choices=[''], style=wx.CB_DROPDOWN)

        st_album = wx.StaticText(self, -1, 'アルバム名: ')
        self.cb_album = wx.ComboBox(self, -1, choices=[''], style=wx.CB_DROPDOWN)

        st_artist = wx.StaticText(self, -1, 'アーティスト名: ')
        self.cb_artist = wx.ComboBox(self, -1, choices=[''], style=wx.CB_DROPDOWN)

        st_genre = wx.StaticText(self, -1, 'ジャンル: ')
        self.cb_genre = wx.ComboBox(self, -1, '選択してください', choices=[''], style=wx.CB_DROPDOWN)

        st_comment = wx.StaticText(self, -1, 'コメント: ')
        self.tc_comment = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

        # タイトル付きBoxSizer
        s_box = wx.StaticBox(self, -1, '曲情報')

        # 配置
        grid = wx.FlexGridSizer(cols=2, gap=(0, 0))
        grid.Add(st_title, flag=wx.ALL, border=10)
        grid.Add(self.cb_title, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_album, flag=wx.ALL, border=10)
        grid.Add(self.cb_album, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_artist, flag=wx.ALL, border=10)
        grid.Add(self.cb_artist, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_genre, flag=wx.ALL, border=10)
        grid.Add(self.cb_genre, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(st_comment, flag=wx.ALL, border=10)
        grid.Add(self.tc_comment, flag=wx.EXPAND | wx.ALL, border=10)

        # 引き伸ばし
        grid.AddGrowableCol(1)

        # 構築
        layout = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        layout.Add(grid, 1)
        self.SetSizer(layout)


class URLTextPanel(wx.Panel):
    """
    URL入力パネル

    Attributes
    ----------
    tc_url : wx.TextCtrl
        URLのテキストボックス
    """

    def __init__(self, parent):
        super().__init__(parent)

        s_box = wx.StaticBox(self, -1, 'SoundCloudのURL')

        # ** 各項目 **
        self.tc_url = wx.TextCtrl(self, -1)
        bt_url_paste = wx.Button(self, -1, label='貼り付け')
        bt_url_clear = wx.Button(self, -1, label='クリア')

        bt_url_paste.Bind(wx.EVT_BUTTON, self.click_bt_url_paste)
        bt_url_clear.Bind(wx.EVT_BUTTON, self.click_bt_url_clear)

        # 配置
        grid = wx.FlexGridSizer(cols=3, gap=(0, 0))
        grid.Add(self.tc_url, flag=wx.EXPAND | wx.ALL, border=10)
        grid.Add(bt_url_paste, flag=wx.ALL, border=10)
        grid.Add(bt_url_clear, flag=wx.ALL, border=10)

        # 引き伸ばし
        grid.AddGrowableCol(0)

        layout = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        layout.Add(grid, 1)
        self.SetSizer(layout)
    
    def click_bt_url_paste(self, event):
        self.tc_url.SetValue(pyperclip.paste())

    def click_bt_url_clear(self, event):
        """ URL入力欄をクリア """
        self.tc_url.Clear()


class ButtonPanel(wx.Panel):
    """ ボタン用 """

    def __init__(self, parent, sc, af):
        super().__init__(parent)

        # scinfo, audiofileのインスタンス(参照)
        self.sc = sc
        self.af = af

        # AudioInfoPanel内のテキストボックス
        self.cb_title = parent.GetParent().ai_panel.cb_title
        self.cb_album = parent.GetParent().ai_panel.cb_album
        self.cb_artist = parent.GetParent().ai_panel.cb_artist
        self.cb_genre = parent.GetParent().ai_panel.cb_genre
        self.tc_comment = parent.GetParent().ai_panel.tc_comment

        # URLPanelのテキストボックス
        self.tc_url = parent.GetParent().url_panel.tc_url

        # ArtworkPanelの画像設定メソッド
        self.set_img = parent.GetParent().aw_panel.set_img

        # ** 各項目 **
        bt_get = wx.Button(self, -1, label='情報取得')
        bt_edit = wx.Button(self, -1, label='書き込み')

        # イベント設定
        bt_get.Bind(wx.EVT_BUTTON, self.click_bt_get)
        bt_edit.Bind(wx.EVT_BUTTON, self.click_bt_edit)

        # 配置
        grid = wx.FlexGridSizer(cols=2, gap=(0, 0))
        grid.Add(bt_get, flag=wx.LEFT, border=200)
        grid.Add(bt_edit, flag=wx.RIGHT, border=200)
        grid.AddGrowableCol(0)

        self.SetSizer(grid)

    def click_bt_get(self, event):
        """ SoundCloudから情報取得 """

        # 各リストを初期化
        titlelist = ['']
        albumlist = ['']
        artistlist = ['']
        genrelist = ['']

        if self.af.filepath == '':
            wx.MessageBox('ファイルを先に選択してください', 'ファイル未選択', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('音声ファイルをドラッグ&ドロップしてください')
            return

        # テキストボックスからURL取得
        url = self.tc_url.GetValue()

        # 情報取得
        try:
            # バー更新
            self.GetTopLevelParent().SetStatusText('SoundCloudから情報を取得しています')

            self.sc.get(url)

            # ドロップダウンリストを更新
            titlelist = [self.af.title] + [self.sc.title]
            albumlist = [self.af.album]
            artistlist = [self.af.artist] + [self.sc.artist]
            genrelist = [self.af.genre] + [self.sc.maintag] + self.sc.taglist

            self.cb_title.SetItems(titlelist)
            self.cb_album.SetItems(albumlist)
            self.cb_artist.SetItems(artistlist)
            self.cb_genre.SetItems(genrelist)

            # 曲情報を入力: 元の情報は保持
            if self.af.title == '':
                self.cb_title.SetValue(self.sc.title)
            else:
                self.cb_title.SetValue(self.af.title)
            
            self.cb_album.SetValue(self.af.album)

            if self.af.artist == '':
                self.cb_artist.SetValue(self.sc.artist)
            else:
                self.cb_artist.SetValue(self.af.artist)

            if self.af.genre == '':
                if self.sc.maintag == '':
                    self.cb_genre.SetLabel('選択してください')
                else:
                    self.cb_genre.SetLabel(self.sc.maintag)
            else:
                self.cb_genre.SetLabel(self.af.genre)

            # すでにSCのURLがコメントにある場合
            if url in self.tc_comment.GetValue():
                url = ''
            # 既にコメントがあるときは、改行してURL挿入
            elif self.tc_comment.GetValue() != '':
                url = '\n' + url
            self.tc_comment.AppendText(url)

            # アートワークを更新
            self.set_img(self.sc.artwork_url)
            self.GetTopLevelParent().SetStatusText('曲情報を確認・編集し、"書き込み"を押してください')

        # エラー
        except scinfo.NotSoundCloudURL:
            wx.MessageBox('SoundCloudのURLを入力してください', '読み込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('情報を取得できませんでした')

        except scinfo.NotTrackURL:
            wx.MessageBox('曲以外のURLが入力されています', '読み込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('情報を取得できませんでした')

        except scinfo.OfflineError:
            wx.MessageBox('オフラインでは情報取得できません\nオンラインで実行してください',
                          '読み込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('情報を取得できませんでした')

    def click_bt_edit(self, event):
        """ 曲情報書き込み """

        # ファイル未選択時
        if self.af.filepath == '':
            wx.MessageBox('ファイルを選択してください', 'ファイル未選択', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('音声ファイルをドラッグ&ドロップしてください')
            return

        # 曲情報を設定
        self.af.title = self.cb_title.GetValue()
        self.af.album = self.cb_album.GetValue()
        self.af.artist = self.cb_artist.GetValue()
        self.af.genre = self.cb_genre.GetValue()
        self.af.comment = self.tc_comment.GetValue()
        self.af.artwork_url = self.sc.artwork_url

        try:
            self.af.edit()
            wx.MessageBox('書き込みが完了しました', '書き込み完了', wx.OK)
            self.GetTopLevelParent().SetStatusText('書き込み完了')
        
        except FileNotFoundError:
            wx.MessageBox('ファイルが見つからないため、曲情報の書き込みができませんでした', 
                        '書き込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('書き込みエラーが発生しました: ファイルが見つかりません')

        except audiofile.URLOpenError:
            wx.MessageBox('オフラインか、その他の理由で画像の書き込みができませんでした',
                        '書き込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('書き込みエラーが発生しました: オンラインになっているか確認してください')

        except:
            wx.MessageBox('曲情報の書き込みができませんでした', '書き込みエラー', wx.ICON_ERROR)
            self.GetTopLevelParent().SetStatusText('書き込みエラーが発生しました')


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
