#!/usr/bin/env python3
# coding: utf-8
import requests,os,regex
import lxml.html

class SoundCloud():
    def __init__(self):
        # self.dr = '任意のディレクトリ'
        self.dr = os.getcwd() + '/trackinfo'

        print('このプログラムは、SoundCloud上の曲のアルバム情報・コメントを取得するプログラムです。')
        print('情報取得したい曲のURLを入力してください。')

        # 対象曲のurl入力
        self.trg_url = input('URL: ')

    # html取得
    def get_html(self):
        # html取得
        trg_html = requests.get(self.trg_url).text
        # 日本語が文字化けするので、ここでデコード
        trg_html = bytes(trg_html,'iso-8859-1').decode('utf-8')
        self.root = lxml.html.fromstring(trg_html)

    # タイトル取得
    def get_title(self):
        return self.root.xpath('string(//img/@alt)')

    # アーティスト名取得
    def get_artist(self):
        return self.root.xpath('string(//div[@itemprop="byArtist"]/meta/@content)')

    # メインタグを取得
    def get_maintag(self):
        return '#' + self.root.xpath('string(//noscript[2]//dd//@href)').replace('/tags/','')

    # サブタグを取得
    def get_subtag():
        tag = root.xpath('string(//script[8])')
        return self.org_subtag(tag)

    # アップロード日時取得
    def get_uploaded(self):
        self.uploaded = self.root.xpath('string(//time)')
        return self.uploaded[0:10]

    # 概要欄を取得
    def get_comment(self):
        return self.root.xpath('string(//meta[@property="og:description"]/@content)')

    # アートワークURLを取得
    def get_artwork_url(self):
        return self.root.xpath('normalize-space(//meta[@property="og:image"]/@content)')

    # サブタグ整理用関数
    def org_subtag(self,tag):
        tag = tag.split('"tag_list":')
        tag = tag[1].split(',')

        # "\ を $ に置き換え
        tag = tag[0].replace('\\"','$').replace('$ ','$~')

        # 正規表現で空白入りのタグを抽出
        space_tag = ''
        space_in = regex.findall('\$[\w\s\p!-/]+\$~',tag)  #記号対応した
        for i in range(len(space_in)):
            tag = tag.replace(space_in[i],'')
            space_tag += ' #' + space_in[i].replace('$','').replace('~','')

        tag = tag.replace('"','').replace(' ',' #')
        return '#' + tag + space_tag

    # 出力
    def output(self):
        self.get_html()
        print("タイトル：" + self.get_title())
        print("アーティスト：" + self.get_artist())
        print("メインタグ：" + self.get_maintag())
        print("サブタグ：" + self.get_subtag())
        print("アップロード日時：" + self.get_uploaded())
        print("概要：\n" + self.get_comment())
        print("アートワーク：" + self.get_artwork_url())

if __name__ == '__main__':
    soundcloud = SoundCloud()
    soundcloud.output()
