# Author: yt-koike
# https://github.com/yt-koike

import cgitb
import sys,io
import sqlite3
from lib import db_filepath,WikiAPI,TableSuite,supported_languages

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cgitb.enable()

db=sqlite3.connect(db_filepath)
api = WikiAPI()
ts=TableSuite(db)
all_word_N = len(ts.words.search("word"))
downloaded_titles = ts.pages.search("title",{"downloaded":1})

template = """
<html><head>
    <meta charset="utf-8">
    <title>Wikiword 検索</title>
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

table{{margin-left:auto;margin-right:auto;}}
-->
</style>
</head>
<body>
    <div id="main">
    <h2>Wikiword 検索</h2>
    <div style="padding: 20px; margin-bottom: 10px; border: 1px dotted #333333;border-radius: 10px;">
        Wikipedia の記事 <strong>{page_N}件</strong> に書かれた単語 <strong>{word_n}語</strong> を検索できます。
        <br>
        対応言語は{languages}です。
        <br><br>
        <div class="hyperlink"><a href="database_update.py">もっと対応単語数を増やす</a></div>
    </div>
    <br>
    <div style="padding: 10px; margin-bottom: 10px; border: 1px solid #333333;border-radius: 10px;">
        <h3>検索欄</h3>
        <form method="GET" action="main.py">
            <input type="text" name="spell" style="width:10em;">
            <button type="submit">検索</button>
            <br>
            検索オプション:
            <input type="radio" name="search" value="match" checked>完全一致
            <input type="radio" name="search" value="partialMatch">部分一致
            <input type="radio" name="search" value="SQL">SQL ワイルドカード
            <br>
            表示オプション:       
            <input type="radio" name="sort" value="word" checked>単語辞書順
            <input type="radio" name="sort" value="title">記事名辞書順
            <input type="radio" name="sort" value="count">使われた回数順(降順)
            <br>
            {lang_options}
            <br><br>
            <div class="hyperlink" style="text-align:right;">
                <a href="https://www.sql-reference.com/select/like.html">SQL ワイルドカードについて</a>
            </div>
        </form>
    </div>
    <div style="padding: 20px; margin-top:100px;margin-bottom: 10px; border: 1px dashed #333333;border-radius: 10px;">
        <h3>初めての方へ</h3>
        <p>
        ここは Wikipedia に載っている記事内の単語を検索するサイトです。
        それにはまず、Wikipedia の記事をダウンロードし、お使いのコンピュータ内のデータベースに保存する必要があります。
        ページ上部の「もっと対応単語数を増やす」を押すと、そのダウンロードを管理するページへ飛びます。
        記事名が列挙されているので、その中から気に入った記事名のものを選択し、表下部の「ダウンロード」ボタンを押しましょう。
        ダウンロードが完了すると、その記事内の単語を検索できるようになります。最初のページに戻り、好きな単語を検索してみましょう。
        </p>
    </div>
    <div style="padding:20px;text-align:right;" class="hyperlink">
    <a href="database_home.py"> データベースの管理画面へ</a>
    </div>
    </div>
</body></html>
"""
lang_options= []
for code,name in supported_languages.items():
    option = f'<input type="checkbox" name="lang" value="{code}" checked>{name}'
    lang_options.append(option)
lang_options_html = "言語: "+" ".join(lang_options)
lang_limit = 4
lang_names = supported_languages.values()
if len(lang_names) <= lang_limit:
    languages_html = ",".join(list(lang_names))
else:
    languages_html = ",".join(list(lang_names)[:lang_limit])+"など"    

result = template.format(page_N=len(downloaded_titles)
                         ,word_n=all_word_N
                         ,languages = languages_html
                         ,lang_options = lang_options_html)
print("Content-type: text/html\n")
print(result)
