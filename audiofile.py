from mutagen import id3, mp3, aiff, flac, mp4
from urllib.request import urlopen
from PIL import Image
import io
import os

# Exceptions
class FileFormatError(Exception):
    """ ファイルフォーマットのエラー """
    pass


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
    artwork : bytes or None
        アートワーク画像
        画像が存在しない場合はNoneが代入される
    """

    def __init__(self):

        self.filepath = ''
        self.fileformat = ''
        self.tags = None

        self.title = ''
        self.album = ''
        self.artist = ''
        #self.albumartist = ''
        self.genre = ''
        self.artwork_url = ''
        self.artwork = None

    def info(self, filepath):
        """
        曲情報を取得する\n
        try - exceptを用いてこのメソッドを用いること\n
        ファイルが発見できない、未対応フォーマットの場合、エラー送出

        Parameters
        ----------
        filepath : str
            音声ファイルのファイルパス
        """

        self.filepath = filepath
        self.fileformat = os.path.splitext(self.filepath)[1]

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
        # ファイルが未存在、未対応フォーマットの場合
        else:
            # エラー送出
            raise FileFormatError('未対応のフォーマットです')


    def mp3info(self):
        """ MP3(ID3)の曲情報を取得 """
        self.tags = mp3.MP3(self.filepath).tags
        # ID3タグが存在しない場合
        if self.tags == None:
            # 空のID3オブジェクトを作成
            self.tags = id3.ID3()
        self.id3info()

    def aiffinfo(self):
        """ AIFFの曲情報を取得 """
        self.tags = aiff.AIFF(self.filepath).tags
        self.id3info()

    def flacinfo(self):
        """ FLACの曲情報を取得 """
        self.tags = flac.FLAC(self.filepath)

        # 各項目取得
        # キーが存在しなかった場合: 半角空白に置き換え
        self.title = self.tags.get('TITLE', ' ')[0]
        self.album = self.tags.get('ALBUM', ' ')[0]
        self.artist = self.tags.get('ARTIST', ' ')[0]
        self.genre = self.tags.get('GENRE', ' ')[0]

        artworks = self.tags.pictures
        artwork = None
        for artwork in artworks:    # 抽出(最後に登録されている画像のみ)
            pass
        if artwork:     # アートワーク画像が存在するか
            self.artwork = artwork.data  # type: bytes
        else:
            self.artwork = None

    def mp4info(self):
        """ MP4(m4a)の曲情報を取得 """
        
        self.tags = mp4.MP4(self.filepath)
        
        # 各項目取得
        self.title = self.tags.get('\xa9nam', ' ')[0]
        self.album = self.tags.get('\xa9alb', ' ')[0]
        self.artist = self.tags.get('\xa9ART', ' ')[0]
        self.genre = self.tags.get('\xa9gen', ' ')[0]

        # アートワーク取得
        artworks = self.tags.get('covr')    # list or None
        artwork = None
        if artworks:
            for artwork in artworks:    # 抽出(最後に登録されている画像のみ)
                pass
        self.artwork = artwork

    def id3info(self):
        """ ID3タグを取得 """

        self.title = str(self.tags.get('TIT2', ''))
        self.album = str(self.tags.get('TALB', ''))
        self.artist = str(self.tags.get('TPE1', ''))
        #self.albumartist = str(self.tags.get('TPE2',''))
        self.genre = str(self.tags.get('TCON', ''))

        # アートワーク取得
        artworks = self.tags.getall('APIC')     # リスト取得
        artwork = None
        for artwork in artworks:    # 抽出
            pass
        if artwork:     # アートワーク画像が存在するか
            self.artwork = artwork.data  # type: bytes
        else:
            self.artwork = None


    def edit(self):
        """
        曲情報を編集する\n
        try - exceptを用いてこのメソッドを用いること\n
        ファイルが発見できない、未対応フォーマットの場合、エラー送出
        """
        # フォーマット判別
        # MP3
        if self.fileformat == '.mp3':
            self.id3edit()
        # AIFF
        elif self.fileformat == '.aiff' \
                or self.fileformat == '.aif' \
                or self.fileformat == '.aifc'\
                or self.fileformat == '.afc':
            self.id3edit()
        # FLAC
        elif self.fileformat == '.flac' \
                or self.fileformat == '.fla':
            self.flacedit()
        # MP4(m4a)
        elif self.fileformat == '.m4a':
            self.mp4edit()
        # ファイルが未存在、未対応フォーマットの場合
        else:
            # エラー送出
            raise

    def id3edit(self):
        """ ID3タグを編集 """

        # ID3タグ書き換え encoding: UTF-16 with BOM (1)
        self.tags['TIT2'] = id3.TIT2(encoding=1, text=self.title)
        self.tags['TALB'] = id3.TALB(encoding=1, text=self.album)
        self.tags['TPE1'] = id3.TPE1(encoding=1, text=self.artist)
        self.tags['TCON'] = id3.TCON(encoding=1, text=self.genre)
        #self.tags['TPE2'] = TPE2(encoding=1, text=self.albumartist)

        # アートワーク書き換え
        if not self.artwork_url == '':   # アートワーク画像のURLがある場合
            # 画像読み込み
            artwork_read = urlopen(self.artwork_url).read()

            # アートワーク初期化
            self.tags.delall('APIC')

            # 画像設定
            self.tags['APIC'] = id3.APIC(
                encoding=1, mime='image/jpeg', type=3, desc='Cover', data=artwork_read)

        # 保存
        self.tags.save(self.filepath)

        # 表示用アートワーク更新
        artworks = self.tags.getall('APIC')  # list
        artwork = None
        for artwork in artworks:    # 抽出
            pass
        if artwork:     # アートワーク画像が存在するか
            self.artwork = artwork.data  # type: bytes
        else:
            self.artwork = None

    def flacedit(self):
        """ FLACの曲情報を編集 """

        # タグ書き換え
        self.tags['TITLE'] = self.title
        self.tags['ALBUM'] = self.album
        self.tags['ARTIST'] = self.artist
        self.tags['GENRE'] = self.genre

        # アートワーク書き換え
        if not self.artwork_url == '':
            # 画像読み込み
            artwork_read = urlopen(self.artwork_url).read()
            # 書き込み用画像オブジェクトを作成
            pic = flac.Picture()
            pic.data = artwork_read
            pic.type = id3.PictureType.COVER_FRONT
            pic.mine = 'image/jpeg'

            # 画像消去
            self.tags.clear_pictures()
            # 画像設定
            self.tags.add_picture(pic)

        # 保存
        self.tags.save(self.filepath)

        # 表示用アートワーク更新
        artworks = self.tags.pictures
        artwork = None
        for artwork in artworks:    # 抽出(最後に登録されている画像のみ)
            pass
        if artwork:     # アートワーク画像が存在するか
            self.artwork = artwork.data  # type: bytes
        else:
            self.artwork = None

    def mp4edit(self):
        """ MP4(m4a)の曲情報を編集 """

        # タグ書き換え
        self.tags['\xa9nam'] = self.title
        self.tags['\xa9alb'] = self.album
        self.tags['\xa9ART'] = self.artist
        self.tags['\xa9gen'] = self.genre

        # アートワーク書き換え
        if not self.artwork_url == '':
            # 画像読み込み
            artwork_read = urlopen(self.artwork_url).read()
            
            # 画像書き換え
            pic = [mp4.MP4Cover(artwork_read, mp4.MP4Cover.FORMAT_JPEG)]    # list
            self.tags['covr'] = pic

        # 保存
        self.tags.save(self.filepath)

        # 表示用アートワーク更新
        artworks = self.tags.get('covr')    # list or None
        artwork = None
        if artworks:
            for artwork in artworks:    # 抽出(最後に登録されている画像のみ)
                pass
        self.artwork = artwork


    def output(self):
        """ テスト出力用 """
        print("pprint:\n{}".format(self.tags.pprint()))
        print("タイトル　　　　　　　: {}".format(self.title))
        print("アルバム名　　　　　　: {}".format(self.album))
        print("アーティスト　　　　　: {}".format(self.artist))
        #print("アルバムのアーティスト: {}".format(self.albumartist))
        print("ジャンル　　　　　　　: {}".format(self.genre))

        # アートワーク表示
        if self.artwork != None:
            im = Image.open(io.BytesIO(self.artwork))
            im.show()
        else:
            print("アートワークなし")


if __name__ == "__main__":
    audiofile = AudioFile()
    audiofile.info(input('対象ファイルパス: '))
    audiofile.output()
