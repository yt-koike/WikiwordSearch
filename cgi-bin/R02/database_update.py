#!/usr/bin/env python3
# Author: yt-koike
# https://github.com/yt-koike

import cgi
import cgitb
import re
import sys,io
import sqlite3
from lib import db_filepath,make_table,TableSuite,WikiAPI,root_url,supported_languages

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cgitb.enable()
db = sqlite3.connect(db_filepath)
ts = TableSuite(db)
form=cgi.FieldStorage()
checked_pageids = form.getvalue("checked_pageids",[])
if type(checked_pageids) == str:
    checked_pageids = [int(checked_pageids)]
elif type(checked_pageids) == list:
    checked_pageids = list(map(int,checked_pageids))

def database_init(ts):
    api = WikiAPI()
    default_page = api.get_contents(["Lists of English words"])[0]
    linked_titles = re.findall('<a href="/wiki/(.*?)" .*>',default_page)
    linked_titles = [x for x in linked_titles if ':' not in x]
    for title in linked_titles:
        ts.new_page(title)

if len(ts.pages.search("title")) == 0:
    database_init(ts)

template = """
<html><head>
    <meta charset="utf-8">
    <title>記事ダウンロードの管理ページ</title>
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

#download {{
width: 30%;
height: 100px;
color: #ffffff;
background-color: #0088ff;
transition: 0.3s;
}}
#download:hover {{
color: #000000;
background-color: #44ff44;
}}
-->
</style>
</head>
<body>
<script language="JavaScript">
    function toggle(source) {{
    checkboxes = document.getElementsByName('checked_pageids');
    for(var i=0, n=checkboxes.length;i<n;i++)
       checkboxes[i].checked = source.checked;
    }}
    </script>
    <h3>{message}</h3>
    <form method="POST" action="database_update.py">
        ダウンロードする記事を指定して下さい。多いほど長く時間がかかります。<br>
        <div style="color:red;">
        ダウンロードを強制的に中断すると、単語の"使われた回数"に誤差が出る可能性があります。
        <br>
        強制的に中断してしまった場合は、再度「新規記事追加」からやり直してください。
        </div><br>
        <input type="checkbox" onClick="toggle(this)" /> すべて選択/選択解除<br/>
        {table}
        <button id="download" type="submit"><h2>ダウンロード</h2></button>
    </form>
    <div class="hyperlink">
        <a href="{root_url}">最初のページへ戻る</a>
    </div>
</body></html>
"""

datas = ts.pages.search("id,title",{"pending":1})
pageids = [x[0] for x in datas]
titles = [x[1] for x in datas]
message = ""
n = len(checked_pageids)
message = "現在以下の記事のダウンロードが保留されています。"
if n > 0:
    failed_titles = ts.fetch_from(checked_pageids)
    message = f"{n-len(failed_titles)}個のダウンロードが完了しました。"
    if len(failed_titles)>0:
        failed_str = "<ul><li>"
        failed_str += "</li><li>".join(failed_titles)
        failed_str += "</li></ul>"
        message += f'<br><div style="color:red">エラー: 以下のサイトのダウンロードに失敗しました。<br>{failed_str}</div>'
    datas = ts.pages.search("id,title",{"pending":1})
    titles = [x[1] for x in datas]
table_list = []
if len(pageids) == 0:
    message = "現在保留されている記事のダウンロードはありません。<br> 表の+マークを押して新しい記事を追加してください。"
else:
    datas = ts.pages.search("id,title,language",{"pending":1})
    for data in datas:
        pageid,title,lang = data
        checkbox = f'<input type="checkbox" name="checked_pageids" value="{pageid}">'
        if lang in supported_languages:
            language = supported_languages[lang]
        else:
            language = f"非対応言語({lang})"
        table_list.append([checkbox,title,language])
table_list.append(["",'<a href="database_add.py">+</a>',""])
table = make_table(table_list,["チェック","記事名","言語"])

result = template.format(message=message,table=table,root_url=root_url)
print("Content-type: text/html\n")
print(result)
