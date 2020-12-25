#!/usr/bin/env python3
# coding: utf-8
import requests,os,regex
import lxml.html

# Exceptions
class NotSoundCloudURL(Exception):
    """
    SoundCloud以外のURLが入力された場合に発生するエラー
    """
    pass

class NotTrackURL(Exception):
    """
    曲以外のURLで処理が進んだ際に発生するエラー
    """
    pass

class OfflineError(Exception):
    """
    オフライン時に発生するエラー
    """
    pass


class SoundCloudInfo():
    """
    SoundCloudから曲情報・アートワーク画像URLを取得する\n
    予期されるエラー:\n
    scinfo.NotSoundCloudURL: 無効なURLが入力されている場合\n
    scinfo.NotTrackURL: 曲以外のURLが入力されている場合\n
    scinfo.OfflineError: オフラインである場合

    Attributes
    -----------
    title : str
        曲のタイトル
    artist : str
        アーティスト名
    maintag : str
        曲のメインタグ（ジャンル）
    taglist : list[str]
        曲のタグリスト
    uploaded : str
        曲のアップロード日時
    overview : str
        曲の概要欄
    artwork_url : str
        SoundCloudのアートワーク画像のURL
    """

    def __init__(self):
        self.title = ''
        self.artist = ''
        self.maintag = ''
        self.taglist = []
        self.uploaded = ''
        self.overview = ''
        self.artwork_url = ''

    def get(self, URL):
        """
        Parameters
        ----------
        URL : str
            SoundCloud上の曲のURL
        """

        # URLチェック
        if not URL.startswith('https://soundcloud.com/'):
            raise NotSoundCloudURL('SoundCloudのURLではありません')

        # html取得
        try:
            trg_html = requests.get(URL).text
        except requests.exceptions.ConnectionError:
            raise OfflineError('オフラインでは曲情報を取得できません')

        # 日本語が文字化けするので、ここでデコード
        trg_html = bytes(trg_html, 'iso-8859-1').decode('utf-8')
        root = lxml.html.fromstring(trg_html)

        # タイトル
        self.title = str(root.xpath('string(//img/@alt)'))

        # アーティスト名
        self.artist = str(root.xpath('string(//div[@itemprop="byArtist"]/meta/@content)'))

        # メインタグ
        self.maintag = str(root.xpath('string(//noscript[2]//dd//@href)').replace('/tags/',''))

        # タグリスト
        #tags = str(root.xpath('string(//script)')) # 取得不可
        tags = trg_html.split('<script>!function')[-1]
        self.taglist = self.org_subtag(tags)

        # アップロード日時
        uploaded = root.xpath('string(//time)')
        self.uploaded = str(uploaded[0:10])

        # 概要欄
        self.overview = str(root.xpath('string(//meta[@property="og:description"]/@content)'))

        # アートワークURL
        self.artwork_url = str(root.xpath('normalize-space(//meta[@property="og:image"]/@content)'))

    def org_subtag(self,tags):
        """
        タグリストの整理
        
        Parameters
        ----------
        tags : str
            htmlから取得した文字列
        """
        # タグを抽出(str)
        tags = tags.split('"tag_list":"')
        # 曲以外のURLだとここでIndexErrorが発生する
        try:
            tags = tags[1].split('",')[0]
        except IndexError:
            raise NotTrackURL('曲以外のURLが入力されています')

        # スペース入りタグを抽出(list)
        space_taglist = regex.findall('\\\\".*?\\\\"', tags)

        # タグ(str)からスペース入りタグを除去
        for i in range(len(space_taglist)):
            tags = tags.replace(space_taglist[i], '')
            
            # スペース入りタグの'\','#' を除去
            space_taglist[i] = space_taglist[i].strip('\\"')
            
        # タグを仕分ける(list化)
        taglist = tags.split(' ')

        # 除去の際に生まれてしまった''要素を削除
        new_taglist = [i for i in taglist if i != '']

        # スペース入りタグリストと連結
        new_taglist += space_taglist

        for i in range(len(new_taglist)):
            # エスケープされた文字列を検出
            escape_str = regex.findall('\\\\u....', new_taglist[i])

            # エスケープ文字列を通常の文字列で置き換え
            for j in range(len(escape_str)):
                # 一旦encode -> decode
                escape_str_dec = escape_str[j].encode().decode('unicode-escape')
                new_taglist[i] = new_taglist[i].replace(escape_str[j], escape_str_dec)
                
        return new_taglist


    def output(self):
        """ テスト出力用 """
        print("タイトル：　　　　{}".format(self.title))
        print("アーティスト：　　{}".format(self.artist))
        print("メインタグ：　　　{}".format(self.maintag))
        print("タグリスト：　　　{}".format(self.taglist))
        print("アップロード日時：{}".format(self.uploaded))
        print("アートワーク：　　{}".format(self.artwork_url))
        print("概要：\n{}".format(self.overview))

if __name__ == '__main__':
    scinfo = SoundCloudInfo()
    scinfo.get(input('対象曲のURL: '))
    scinfo.output()
