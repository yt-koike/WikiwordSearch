# Author: yt-koike
# https://github.com/yt-koike

import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
template = """
<html>
    <head>
        <meta charset="utf-8">
        <title>
            Database Home
        </title>
        <style type="text/css">
        <!--
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
        <form method="POST" name="form1" action="database_SQL.py">
            <input type="hidden" name="sql" value="SELECT title,language FROM pages WHERE downloaded = 1">
            <a href="javascript:form1.submit()">ダウンロード済み記事一覧</a>
        </form>
        <a href="database_update.py">新しい記事をダウンロード</a><br>
        <a href="database_SQL.py">データベース内で SQL 検索</a>
    </body>
</html>
"""

print("Content-type: text/html\n")
print(template)
