from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, TCON, APIC
from PIL import Image
from urllib.request import urlopen
import io

class AudioFile():
    """
    音声ファイルのID3タグを取得・編集する

    Attributes
    -----------
    title : str
        曲のタイトル
    album : str
        アルバム名
    artist : str
        アーティスト名
    genre : str
        ジャンル
    artwork_url : str
        SoundCloudのアートワーク画像のURL
    """
    
    def __init__(self, filepath):
        """
        Parameters
        ----------
        filepath : str
            音声ファイルのファイルパス
        """
        # ID3読み込み
        self.tags = ID3(filepath)

        # タイトル
        self.title = str(self.tags.get('TIT2',''))
        # アルバム名
        self.album = str(self.tags.get('TALB',''))
        # アーティスト
        self.artist = str(self.tags.get('TPE1',''))
        # アルバムのアーティスト
        #self.albumartist = str(self.tags.get('TPE2',''))
        # ジャンル
        self.genre = str(self.tags.get('TCON',''))
        # アートワーク画像のURL
        self.artwork_url = ''
        # アートワーク(bytes, 表示用) self.artwork
        artworks = self.tags.getall('APIC')
        for self.artwork in artworks:
            pass
    
    def edit(self):
        """ ID3タグ書き込み用 """

        # ID3タグ書き換え encoding: UTF-16 with BOM (1)
        self.tags['TIT2'] = TIT2(encoding=1, text=self.title)
        self.tags['TALB'] = TALB(encoding=1, text=self.album)
        self.tags['TPE1'] = TPE1(encoding=1, text=self.artist)
        self.tags['TCON'] = TCON(encoding=1, text=self.genre)
        #self.tags['TPE2'] = TPE2(encoding=1, text=self.albumartist)

        # アートワーク
        if not self.artwork_url == '':   # アートワーク画像のURLがある場合
            # 画像読み込み
            artwork_read = urlopen(self.artwork_url).read()

            # 画像設定
            self.tags['APIC'] = APIC(
                encoding=1, mime='image/jpeg', type=3, desc='Cover', data=artwork_read)

            # アートワーク初期化
            self.tags.delall('APIC')

        # 保存
        self.tags.save()

        # アートワーク更新（表示用）
        artworks = self.tags.getall('APIC')
        for self.artwork in artworks:
            pass
    
    def output(self):
        """ テスト出力用 """
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
    #audiofile.edit()
