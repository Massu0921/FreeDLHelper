#!/usr/bin/env python3
# coding: utf-8
import requests,os,regex,time
import lxml.html

class SoundCloudInfo():
    def __init__(self, URL=input('対象曲のURL: ')):  # 対象曲のurl入力 (引数)
        # url設定
        self.trg_url = URL
        # html取得
        trg_html = requests.get(self.trg_url).text
        # 日本語が文字化けするので、ここでデコード
        trg_html = bytes(trg_html, 'iso-8859-1').decode('utf-8')
        self.root = lxml.html.fromstring(trg_html)

        # タイトル
        self.title = self.root.xpath('string(//img/@alt)')

        # アーティスト名
        self.artist = self.root.xpath('string(//div[@itemprop="byArtist"]/meta/@content)')

        # メインタグ
        self.maintag = '#' + self.root.xpath('string(//noscript[2]//dd//@href)').replace('/tags/','')

        # サブタグ
        tag = self.root.xpath('string(//script[8])')
        self.subtag = self.org_subtag(tag)

        # アップロード日時
        uploaded = self.root.xpath('string(//time)')
        self.uploaded = uploaded[0:10]

        # 概要欄
        self.comment = self.root.xpath('string(//meta[@property="og:description"]/@content)')

        # アートワークURL
        self.artwork_url = self.root.xpath('normalize-space(//meta[@property="og:image"]/@content)')

    # サブタグ整理用関数
    def org_subtag(self,tag):
        tag = tag.split('"tag_list":')
        tag = tag[1].split(',')

        # "\ を $ に置き換え
        tag = tag[0].replace('\\"','$').replace('$ ','$~')

        # 正規表現で空白入りのタグを抽出
        space_tag = ''
        space_in = regex.findall('\$[\w\s\p!-/]+\$~',tag)  # 記号対応
        for i in range(len(space_in)):
            tag = tag.replace(space_in[i],'')
            space_tag += ' #' + space_in[i].replace('$','').replace('~','')

        tag = tag.replace('"','').replace(' ',' #')
        return '#' + tag + space_tag

    # 出力
    def output(self):
        print("タイトル：　　　　{}".format(self.title))
        print("アーティスト：　　{}".format(self.artist))
        print("メインタグ：　　　{}".format(self.maintag))
        print("サブタグ：　　　　{}".format(self.subtag))
        print("アップロード日時：{}".format(self.uploaded))
        print("アートワーク：　　{}".format(self.artwork_url))
        print("概要：\n{}".format(self.comment))

if __name__ == '__main__':
    scinfo = SoundCloudInfo()
    scinfo.output()
