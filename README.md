# SC-trackinfo
SoundCloud上のトラックの情報を取得します。

# 使用モジュール
## os
## requests
`pip3 install requests`
## lxml
`pip3 install lxml`
## regex
`pip3 install regex`

# 文字化け対処
以下の構文で対処
~~~python
bytes('対象文字列','iso-8859-1').decode('utf-8')
~~~
