#!/usr/bin/env python3
# coding: utf-8
import requests,os
import lxml.html

class SoundCloud():
    def __init__(self):
        # dr = '任意のディレクトリ'
        dr = os.getcwd() + '/trackinfo'

        print('このプログラムは、SoundCloud上の曲のアルバム情報・コメントを取得するプログラムです。')
        print('情報取得したい曲のURLを入力してください。')

        # 対象曲のurl入力
        self.trg_url = input('URL: ')

    def getinfo(self):
        # html取得
        trg_html = requests.get(self.trg_url).text
        root = lxml.html.fromstring(trg_html)

        # タイトル・アーティスト名取得
        self.title = root.xpath('string(//img/@alt)')
        self.artist = root.xpath('string(//div[@itemprop="byArtist"]/meta/@content)')

        # メインタグを取得
        self.maintag = root.xpath('string(//noscript[2]//dd//@href)').replace('/tags/','')

        #サブタグを取得
        tag = root.xpath('string(//script[8])')
        tag = tag.split('"tag_list":')
        tag = tag[1].split(',')
        #ここがうまくできない
        self.subtag = tag[0].replace('\\"',' ').replace('  ','#').replace('"','#')

        # アップロード日時取得
        self.uploaded = root.xpath('string(//time)')
        self.uploaded = self.uploaded[0:10]

        # 概要欄を取得
        self.comment = root.xpath('string(//meta[@property="og:description"]/@content)')

        # アートワークURLを取得
        self.img_url = root.xpath('normalize-space(//img/@src)')


    def output(self):
        self.getinfo()
        print("タイトル：" + self.title)
        print("アーティスト：" + self.artist)
        print("メインタグ：" + self.maintag)
        print("サブタグ：" + self.subtag)
        print("アップロード日時：" + self.uploaded)
        print("コメント：\n" + self.comment)
        print("アートワーク：" + self.img_url)

if __name__ == '__main__':
    soundcloud = SoundCloud()
    soundcloud.output()
