#!/usr/bin/env python3
# Author: yt-koike
# https://github.com/yt-koike

import cgi
import cgitb
import sys,io
import sqlite3
from lib import db_filepath,make_table,root_url

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cgitb.enable()
form=cgi.FieldStorage()

template = """
<html><head>
    <meta charset="utf-8">
    <title>データベース検索</title>
<style type="text/css">
<!--
#main {{
  text-align: center;
}}
a {{
padding: 9px 2px 8px 2px;
width: 250px;
border: solid 2px #222222;
text-decoration: none;
color: #000000;
background-color: #FFFFFF;
transition: 0.3s;
}}

a:hover {{
color: #ffffff;
background-color: #000000;
}}

-->
</style>
</head>
<body>
    <p>データベースには以下の３つのテーブルがあります。
    <ul>
        <li>words : 単語など</li>
        <li>pages : 記事情報など</li>
        <li>pagewords : 各記事にかかれた単語とその回数など</li>
    </ul>
    </p>
    <form method="POST" action="database_SQL.py">
        SQLクエリを入力してください。例:SELECT * FROM pages<br>
        <input type="text" name="sql" style="width:40em;" value="{sql}">
        <button type="submit" name="search" value="1">SQL 実行</button>
    </form>
    <a href="{root_url}">最初のページへ戻る</a>
    <p>{results}</p>
    <a href="{root_url}">最初のページへ戻る</a>
</body></html>
"""
def make_html(db_filepath, sql):
    result = ""
    con=sqlite3.connect(db_filepath)
    cur=con.cursor()
    try:
        cur.execute(sql)
        datas = [list(x) for x in cur.fetchall()]
        result = make_table(datas,[desc[0] for desc in cur.description])
    except sqlite3.Error as err:
        result = '<p style="color:#FF0000";>'+ str(err) + "</p>"
    return result
result_html = ""
sql = form.getvalue("sql", "")
if len(sql) > 0:
    result_html = make_html(db_filepath,sql)
result = template.format(results = result_html,sql=sql,root_url=root_url)
print("Content-type: text/html\n")
print(result)
