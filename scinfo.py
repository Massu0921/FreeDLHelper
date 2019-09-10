#!/usr/bin/env python3
# coding: utf-8
import requests,os,regex,time
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

    def __init__(self, URL):
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
        self.root = lxml.html.fromstring(trg_html)

        # タイトル
        self.title = self.root.xpath('string(//img/@alt)')

        # アーティスト名
        self.artist = self.root.xpath('string(//div[@itemprop="byArtist"]/meta/@content)')

        # メインタグ
        self.maintag = self.root.xpath('string(//noscript[2]//dd//@href)').replace('/tags/','')

        # タグリスト
        tags = self.root.xpath('string(//script[8])')
        self.taglist = self.org_subtag(tags)

        # アップロード日時
        uploaded = self.root.xpath('string(//time)')
        self.uploaded = uploaded[0:10]

        # 概要欄
        self.overview = self.root.xpath('string(//meta[@property="og:description"]/@content)')

        # アートワークURL
        self.artwork_url = self.root.xpath('normalize-space(//meta[@property="og:image"]/@content)')

    def org_subtag(self,tags):
        """
        タグリストの整理
        
        Parameters
        ----------
        tag : str
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
            tags = tags.replace(space_taglist[i] + ' ', '')
            
            # スペース入りタグの'\','#' を除去
            space_taglist[i] = space_taglist[i].replace('\\','').replace('"', '')
            
        # タグを仕分ける(list化)
        taglist = tags.split(' ')
        # スペース入りタグリストと連結
        taglist += space_taglist
                
        return taglist


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
    scinfo = SoundCloudInfo(input('対象曲のURL: '))
    scinfo.output()
