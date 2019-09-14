# FreeDLHelper
SoundCloudから楽曲情報・アートワーク画像を取得し、Free DLなどした音声ファイルに不足情報を追加するツールです。

## 環境
- Windows10 Python 3.7.4 \
macOSでの動作は確認していません

## ライブラリ
- requests
> `py -m pip install requests`
- lxml
> `py -m pip install lxml`
- regex
> `py -m pip install regex`
- mutagen
> `py -m pip install mutagen`
- wxPython
> `py -m pip install wxpython`

## 使用方法
1. 上記のライブラリをインストールし、`py main.py` を実行
2. 曲情報を追加したい音声ファイルを、選択ダイアログまたはドラッグ&ドロップで選択
3. SoundCloudの対象曲のURLを貼り付け、"情報取得"を押して曲情報を取得
4. 取得した曲情報を確認・編集し、"書き込み"を押して音声ファイルに曲情報を書き込む
