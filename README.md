# FreeDLHelper v1.1b
SoundCloudから楽曲情報・アートワーク画像を取得し、Free DLなどした音声ファイルに不足情報を追加するツールです。

## 環境
- Windows10 Python 3.7.4 \
macOSでの動作は確認していません

## インストールが必要なライブラリ
- Requests https://2.python-requests.org/en/master/
> `py -m pip install requests`
- lxml https://lxml.de/
> `py -m pip install lxml`
- regex https://bitbucket.org/mrabarnett/mrab-regex/src/default/
> `py -m pip install regex`
- mutagen https://github.com/quodlibet/mutagen
> `py -m pip install mutagen`
- wxPython http://wxPython.org/
> `py -m pip install wxpython`

## 使用方法
1. 上記のライブラリをインストールし、`py main.py` を実行
2. 曲情報を追加したい音声ファイルを、選択ダイアログまたはドラッグ&ドロップで選択
3. SoundCloudの対象曲のURLを貼り付け、"情報取得"を押して曲情報を取得
4. 取得した曲情報を確認・編集し、"書き込み"を押して音声ファイルに曲情報を書き込む

## 更新情報
- SoundCloudからの情報取得時に、元の曲情報を保持するように
- URL入力欄をクリアするボタンを追加