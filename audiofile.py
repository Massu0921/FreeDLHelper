from mutagen import id3, aiff, flac, mp4
from urllib.request import urlopen
from PIL import Image
import io
import os


class AudioFile():
    """
    音声ファイルの曲情報を取得・編集する

    Attributes
    -----------
    filepath : str
        音声ファイルのパス
    fileformat : str
        音声ファイルの拡張子
    title : str
        曲のタイトル
    album : str
        アルバム名
    artist : str
        アーティスト名
    genre : str
        ジャンル
    artwork_url : str
        アートワーク画像のURL
    artwork : somecase
        アートワーク画像
    """

    def __init__(self, filepath):
        """
        Parameters
        ----------
        filepath : str
            音声ファイルのファイルパス
        """
        self.filepath = filepath
        self.fileformat = os.path.splitext(self.filepath)[1]

        self.title = ''
        self.album = ''
        self.artist = ''
        self.albumartist = ''
        self.genre = ''
        self.artwork_url = ''
        self.artwork = None

        # フォーマット判別
        # MP3
        if self.fileformat == '.mp3':
            self.mp3info()
        # AIFF
        elif self.fileformat == '.aiff' \
                or self.fileformat == '.aif' \
                or self.fileformat == '.aifc'\
                or self.fileformat == '.afc':
            self.aiffinfo()
        # FLAC
        elif self.fileformat == '.flac' \
                or self.fileformat == '.fla':
            self.flacinfo()
        # MP4(m4a)
        elif self.fileformat == '.m4a':
            self.mp4info()
        else:
            print('未対応フォーマット')
            exit()

    def mp3info(self):
        """ MP3(ID3)の曲情報を取得 """
        self.tags = id3.ID3(self.filepath)
        self.id3info()

    def aiffinfo(self):
        """ AIFFの曲情報を取得 """
        self.tags = aiff.AIFF(self.filepath).tags
        self.id3info()

    def flacinfo(self):
        """ FLACの曲情報を取得 """
        pass

    def mp4info(self):
        """ MP4(m4a)の曲情報を取得 """
        pass

    def id3info(self):
        """ ID3タグを取得 """
        # タイトル
        self.title = str(self.tags.get('TIT2', ''))
        # アルバム名
        self.album = str(self.tags.get('TALB', ''))
        # アーティスト
        self.artist = str(self.tags.get('TPE1', ''))
        # アルバムのアーティスト
        #self.albumartist = str(self.tags.get('TPE2',''))
        # ジャンル
        self.genre = str(self.tags.get('TCON', ''))
        # アートワーク画像のURL
        self.artwork_url = ''
        # アートワーク(bytes, 表示用 最後に登録された画像のみ) self.artwork.data
        artworks = self.tags.getall('APIC')
        for self.artwork in artworks:
            pass

    def id3edit(self):
        """ ID3タグを編集 """

        # ID3タグ書き換え encoding: UTF-16 with BOM (1)
        self.tags['TIT2'] = id3.TIT2(encoding=1, text=self.title)
        self.tags['TALB'] = id3.TALB(encoding=1, text=self.album)
        self.tags['TPE1'] = id3.TPE1(encoding=1, text=self.artist)
        self.tags['TCON'] = id3.TCON(encoding=1, text=self.genre)
        #self.tags['TPE2'] = TPE2(encoding=1, text=self.albumartist)

        # アートワーク
        if not self.artwork_url == '':   # アートワーク画像のURLがある場合
            # 画像読み込み
            artwork_read = urlopen(self.artwork_url).read()

            # 画像設定
            self.tags['APIC'] = id3.APIC(
                encoding=1, mime='image/jpeg', type=3, desc='Cover', data=artwork_read)

            # アートワーク初期化
            self.tags.delall('APIC')

        # 保存
        self.tags.save()

        # アートワーク更新（表示用）
        artworks = self.tags.getall('APIC')
        for self.artwork in artworks:
            pass

    def flacedit(self):
        """ FLACの曲情報を編集 """
        pass

    def mp4edit(self):
        """ MP4(m4a)の曲情報を編集 """
        pass

    def output(self):
        """ テスト出力用 """
        print("pprint:\n{}".format(self.tags.pprint()))
        print("タイトル　　　　　　　: {}".format(self.title))
        print("アルバム名　　　　　　: {}".format(self.album))
        print("アーティスト　　　　　: {}".format(self.artist))
        #print("アルバムのアーティスト: {}".format(self.albumartist))
        print("ジャンル　　　　　　　: {}".format(self.genre))

        # アートワーク表示
        try:
            im = Image.open(io.BytesIO(self.artwork.data))
            im.show()
        except:
            print("アートワークなし")


if __name__ == "__main__":
    audiofile = AudioFile(input('対象ファイルパス: '))
    audiofile.output()
