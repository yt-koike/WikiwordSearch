#!/usr/bin/env python3
# Author: yt-koike
# https://github.com/yt-koike
import cgi
import cgitb
import sys,io
import sqlite3
from lib import db_filepath,make_table,lowercase,TableSuite,supported_languages

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cgitb.enable()
form=cgi.FieldStorage()
spell = form.getvalue("spell", "")
search = form.getvalue("search", "match")
sort = form.getvalue("sort", "word")
languages = form.getvalue("lang",[])
if type(languages) == str:
    languages = [languages]

spell = lowercase(spell)
db = sqlite3.connect(db_filepath)
ts = TableSuite(db)
wordids = []
if len(spell) > 0:
    if search in ["match","SQL"]:
        for lang in languages:
            wordids += ts.words.getSimilarWordIds(spell,lang)
    elif search in ["partialMatch"]:
        for lang in languages:
            wordids += ts.words.getSimilarWordIds(f"%{spell}%",lang)
result = []
for wordid in wordids:
    wordinfo = ts.words.getInfo(wordid)
    if len(wordinfo) == 0:
        continue
    word = wordinfo["word"]
    language_code = wordinfo["language"]
    if language_code in supported_languages:
        language = supported_languages[language_code]
    else:
        language = f"未対応言語{language_code}"
    pageids = ts.pagewords.getPageIds(wordid)
    for pageid in pageids:
        pageinfo = ts.pages.getInfo(pageid)
        if len(pageinfo) >0:
            title = pageinfo["title"]
            count = ts.pagewords.get_count(wordid,pageid)
            url = f'http://{language_code}.wikipedia.org/wiki/{title}'
            titled_link = f'<a href="{url}">{title}</a>'
            result.append((word,titled_link,count,language))
key = lambda x:x[["word","title","count"].index(sort)]
reverse = False
if sort in ["count"]:
    reverse = True
result.sort(key=key,reverse=reverse)

template = """
<html><head>
    <meta charset="utf-8">
    <title>検索結果</title>
    <style type="text/css">
    <!--   
        #main{{text-align:center}}
        table{{margin-left:auto;margin-right:auto;}}
    -->
    </style>
</head>

<body>
    <div id="main">
    <h2>{message}</h2>
    <p>使われた総回数:{total}</p>
    <p>{results}</p>
    </div>
</body></html>
"""
total = sum([x[2] for x in result])
results = make_table(result,["単語","記事名","使われた回数","言語"])
search_names = {'match':'完全一致'
                ,'partialMatch':'部分一致'
                ,'SQL':'SQLワイルドカード'}
message = f"{spell}の検索結果({search_names[search]})"
html = template.format(message=message,total = total,results = results)

print("Content-type: text/html\n")
print(html)
