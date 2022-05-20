# Author: yt-koike
# https://github.com/yt-koike

import cgi
import cgitb
import sys,io
import sqlite3
import re
import urllib.parse
from lib import db_filepath,TableSuite,supported_languages

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cgitb.enable()
form=cgi.FieldStorage()
url = form.getvalue("url", None)

template = """
<html><head>
    <meta charset="utf-8">
    <title>新規記事追加</title>
    <style type="text/css">
        <!--
        #main {{
        text-align: center;
        }}
        .hyperlink a {{
        padding: 9px 2px 8px 2px;
        width: 250px;
        border: solid 2px #222222;
        text-decoration: none;
        color: #000000;
        background-color: #FFFFFF;
        transition: 0.3s;
        }}

        .hyperlink a:hover {{
        color: #ffffff;
        background-color: #000000;
        }}
        -->
    </style>
</head>
<body>
    <form method="GET" action="database_add.py">
        <h3>新規記事追加</h3>
        追加方法:記事のURLを入力してください。例:https://en.wikipedia.org/wiki/Wikipedia
        <br>
        <input type="text" name="url" placeholder="記事のURLを入力してください。" style="width:20em;">
        <button type="submit">追加</button>
    </form>
    <h3>{message}</h3>
    <div class="hyperlink">
        <a href="database_update.py">戻る</a>
    </div>
</body></html>
"""
message = ""
if url is not None:
    url = url.replace("http://","").replace("https://","")
    try:
        lang = url.split('.')[0]
        title = urllib.parse.unquote(url.split('/')[2])
    except:
        message = "エラー:不正な URL が入力されました。"
    else:
        if url.startswith(lang+".wikipedia.org/wiki/"):
            if not lang in supported_languages:
                message = "エラー:非対応言語の記事です。"
            else:
                db = sqlite3.connect(db_filepath)
                ts = TableSuite(db)    
                ts.new_page(title,lang)
                message = f"新規記事「{title}」がダウンロードキューに追加されました。"
        else:
            message = "エラー: Wikipedia ではない URL が入力されました。"
            
languages_html =""
for code,name in supported_languages.items():
    languages_html += f'<option value="{code}">{name}</option>'
result = template.format(message=message,languages = languages_html)
print("Content-type: text/html\n")
print(result)
