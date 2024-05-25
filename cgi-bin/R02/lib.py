#!/usr/bin/env python3
# Author: yt-koike
# https://github.com/yt-koike

from sqlite3 import OperationalError
import re
import requests
import json
import time

root_url = "toppage.py"
db_filepath = "Wikiword.sqlite3"
supported_languages = {"en":"英語",
             "fr":"フランス語",
             "es":"スペイン語",
             "de":"ドイツ語",
             "ru":"ロシア語",
             "it":"イタリア語"
             }

def is_alphabet(ch):
    code = ord(ch)
    detect_fs = [lambda code:ord('A')<= code <=ord('Z')
                 ,lambda code:ord('a')<= code <=ord('z')
                 ,lambda code:0xC0 <= code <= 0xD6 #Latin-1
                 ,lambda code:0xD8 <= code <= 0xF6 #Latin-1
                 ,lambda code:0xF8 <= code <= 0xFF #Latin-1
                 ,lambda code:0x100 <= code <= 0x17F #European Latin
                 ,lambda code:0x180 <= code <= 0x1BF #Non-European & historic Latin
                 ,lambda code:0x370 <= code <= 0x3FF #Greek
                 ,lambda code:0x400 <= code <= 0x4FF #Cyrillic
                ]
    for f in detect_fs:
        if f(code):
            return True
    return False
def is_number(ch):
    return ord('0')<=ord(ch)<=ord('9')

def lowercase(string):
    result = ""
    for ch in string:
        x = ord(ch)
        if ord('A')<=x<=ord('Z'):
            x = x - ord('A') + ord('a')
        if 0xC0 <= x <= 0xDE: #Latin-1
            x = x - 0xC0 + 0xE0
        if 0x100 <= x <= 0x17E and x%2 == 0: #Latin
            x += 1
        if x == 0x386: #Greek
            x = 0x3AC
        if 0x391 <= x <= 0x3AB: #Greek
            x = x - 0x391 + 0x3B1
        if 0x410 <= x <= 0x42F: #Cyrillic
            x = x - 0x410 + 0x430
        if 0x400 <= x <= 0x40F: #Cyrillic
            x = x - 0x400 + 0x450
        result += chr(x)
    return result
#--------------------------------
#API
class WikiAPI:
    def __init__(self):
        pass

    def get_contents(self,titles,lang = "en"):
        limit = 3
        wait_time = 5
        result = []
        partitions = []
        for i in range(0,len(titles),limit):
            partitions.append(titles[i:i+limit])
        for i in range(len(partitions)):
            if i > 0:
                time.sleep(wait_time)
            part = partitions[i]
            for title in part:
                try:
                    response = requests.get(
                        url=f"https://{lang}.wikipedia.org/w/api.php",
                        params={"action":"parse",
                                "page":title,
                                "prop":"text",
                                "formatversion":2,
                                "format":"json"
                                }
                    )
                    content = json.loads(response.text)
                except:
                    result.append("")
                    continue
                if "error" in content:
                    result.append("")
                    continue
                html = content["parse"]["text"]
                result.append(html)
        return result
    
    def extract(self,html):
        text = html
        text = text.replace('\n',' ')
        text = text.replace('\r',' ')
        del_patterns = [r'<style .*?>.*?</style>'
                        ,r'<!--.*?-->'
                        ,r'<.*?>'
                        ,r'&#.*?;']
        for del_pattern in del_patterns:
            cleanr = re.compile(del_pattern)
            text = re.sub(cleanr,' ',text)
        def letter_filter(ch): 
            ignore_list = [' ',"'","-","’"]
            if ch in ignore_list:
                return ch
            if is_alphabet(ch):
                return ch
            if is_number(ch):
                return ch
            if ch == '\n':
                return ' '
            return ' '
        text = ''.join(map(letter_filter,text))
        raw_text = text
        return raw_text

    def wordcount(self,raw_text):
        lowered_raw_text = lowercase(raw_text)
        words = lowered_raw_text.split(' ')
        words = [word for word in words if word != '']
        result = {}
        for word in words:
            if word not in result:
                result[word] = 1
            else:
                result[word] += 1
        return result
#--------------------------------
#DATABASE
class Table:
    def __init__(self,DB,table_name):
        self.DB = DB
        self.table_name = table_name

    def quotize(self,data):
        if type(data) == str:
            data = f'"{data}"'
        elif type(data) == int:
            data = f'{data}'
        return data

    def create(self,column_dict):
        names = list(column_dict.keys())
        types = list(column_dict.values())
        args = [f"{names[i]} {types[i]}" for i in range(len(names))]
        args_str = ','.join(args)
        cur = self.DB.cursor()
        sql = f"CREATE TABLE {self.table_name} ({args_str});"
        try:
            cur.execute(sql)        
        except OperationalError as e:
            pass
        self.commit()

    def insert(self,request):
        columns = list(request.keys())
        datas = list(map(self.quotize,list(request.values())))
        columns_str = ','.join(columns)
        datas_str = ','.join(datas)
        cur = self.DB.cursor()
        sql = f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({datas_str});"
        cur.execute(sql)
        self.commit()

    def search(self,sel,query = {'"1"':"1"},operator = '='):
        columns = list(query.keys())
        datas = list(map(self.quotize,list(query.values())))
        conditions = [f"{columns[i]} {operator} {datas[i]}" for i in range(len(datas))]
        conditions_str = ' AND '.join(conditions)
        cur = self.DB.cursor()
        cur.execute(f"SELECT {sel} FROM {self.table_name} WHERE {conditions_str};")
        return cur.fetchall()

    def update(self,request,query = {'"1"':"1"}):
        columns = list(query.keys())
        datas = list(map(self.quotize,list(query.values())))
        conditions = [f"{columns[i]} = {datas[i]}" for i in range(len(datas))]
        conditions_str = ' AND '.join(conditions)
        cur = self.DB.cursor()
        req_columns = list(request.keys())
        req_datas = list(map(self.quotize,list(request.values())))
        req = [f"{req_columns[i]} = {req_datas[i]}" for i in range(len(req_datas))]
        req_str = ','.join(req)
        cur.execute(f"UPDATE {self.table_name} SET {req_str} WHERE {conditions_str};")
        self.commit()

    def delete(self,query = {'"1"':"1"},operator = '='):
        columns = list(query.keys())
        datas = list(map(self.quotize,list(query.values())))
        conditions = [f"{columns[i]} {operator} {datas[i]}" for i in range(len(datas))]
        conditions_str = ' AND '.join(conditions)
        cur = self.DB.cursor()
        cur.execute(f"DELETE FROM {self.table_name} WHERE {conditions_str};")
        self.commit()
        
    def commit(self):
        self.DB.commit()


class PageTable(Table):
    def __init__(self,DB):
        super().__init__(DB,"pages")
        self.create({"id":"int",
                     "title":"text",
                     "downloaded":"int",
                     "pending":"int",
                     "language":"text",
                     "error":"int"})
        x = self.search("max(id)")[0][0]
        if x is None:
            self.newpage_id = 0
        else:
            self.newpage_id = x + 1
    
    def new_page(self,title,lang = "en"):
        pages = self.search("*",{"title":title,"language":lang})
        if len(pages) == 0:
            self.insert({"id":self.newpage_id,
                        "title":title,
                        "downloaded":0,
                        "pending":1,
                        "language":lang,
                        "error":0
                        })
            self.newpage_id += 1
            return self.newpage_id - 1
        else:
            self.update({"downloaded":0,"pending":1,"error":0}
                        ,{"title":title,"language":lang})
            return pages[0][0]

    def getInfo(self,pageid):
        columns = ["id","title","language"]
        db_data = self.search(",".join(columns),{"id":pageid})
        if len(db_data) == 0:
            return {}
        db_data = db_data[0]
        result = {}
        for i in range(len(columns)):
            result[columns[i]] = db_data[i]
        return result
    
    def getIdByTitle(self,title,lang):
        x = self.search("id",{"title":title,"language":lang})
        if len(x) == 0:
            return -1
        else:
            return x[0][0]
    
    def get_undownloaded_titles(self):
        titles = self.search("title",{"downloaded":0})
        return [x[0] for x in titles]

    def get_link(self,pageid):
        title = self.search("title",{"id":pageid})
        lang = self.search("language",{"id":pageid})
        if len(title) > 0 and len(lang) > 0:
            title = title[0][0]
            lang = lang[0][0]
            return f"https://{lang}.wikipedia.org/wiki/{title}"
        return None

class PageWordTable(Table):
    def __init__(self,DB):
        super().__init__(DB,"pagewords")
        self.create({"wordid":"int","pageid":"int","count":"int"})

    def new_row(self,wordid,pageid,count = 1):
        self.insert({"wordid":wordid,
                     "pageid":pageid,
                     "count":count})

    def get_count(self,wordid,pageid):
        x = self.search("count",
                            {"wordid":wordid,"pageid":pageid})
        if len(x) == 0:
            count = -1
        else:
            count = x[0][0]
        return count
    
    def set_count(self,wordid,pageid,count):
        if self.get_count(wordid,pageid) == -1:
            self.insert({"wordid":wordid,
                         "pageid":pageid,
                         "count":count})
            return
        self.update({"count":count},
                    {"wordid":wordid,"pageid":pageid})

    def getPageIds(self,word_id):
        page_ids = self.search("pageid",{"wordid":word_id})
        return [x[0] for x in page_ids]

    def getWordIds(self,page_id):
        word_ids = self.search("wordid",{"pageid":page_id})
        return [x[0] for x in word_ids]

class WordTable(Table):
    def __init__(self,DB):
        super().__init__(DB,"words")
        self.create({"id":"int","word":"text","language":"text"})
        x = self.search("max(id)")[0][0]
        if x is None:
            self.newword_id = 0
        else:
            self.newword_id = x + 1
    
    def new_word(self,word,lang):
        if len(self.search("*",{"word":word,"language":lang})) == 0:
            self.insert({"id":self.newword_id,"word":word,"language":lang})
            self.newword_id += 1
            return self.newword_id - 1
    
    def getIdByWord(self,word,lang):
        x = self.search("id",{"word":word,"language":lang})
        if len(x) == 0:
            return -1
        else:
            return x[0][0]

    def getSimilarWordIds(self,word,lang):
        ids = self.search("id",{"word":word,"language":lang},"LIKE")
        ids = [x[0] for x in ids]
        return ids

    def getInfo(self,wordid):
        columns = ["id","word","language"]
        db_data = self.search(",".join(columns),{"id":wordid})
        if len(db_data) == 0:
            return {}
        db_data = db_data[0]
        result = {}
        for i in range(len(columns)):
            result[columns[i]] = db_data[i]
        return result

class TableSuite:
    def __init__(self,DB):
        self.DB = DB
        self.words = WordTable(DB)
        self.pages = PageTable(DB)
        self.pagewords = PageWordTable(DB)
        self.DB.commit()
    
    def register(self,word,page_title,count,lang):
        wordid = self.words.getIdByWord(word,lang)
        if wordid == -1:
            wordid = self.words.new_word(word,lang)
        pageid = self.pages.getIdByTitle(page_title,lang)
        if pageid == -1:
            pageid = self.pages.new_page(page_title,lang)
        old_count = self.pagewords.get_count(wordid,pageid)
        if old_count == -1:
            old_count = 0
        new_count = old_count + count
        self.pagewords.set_count(wordid,pageid,new_count)
        self.DB.commit()
    
    def new_page(self,title,lang = "en"):
        page_id = self.pages.new_page(title,lang)
        self.pagewords.delete({"pageid":page_id})

    def fetch_from(self,pageids):
        api = WikiAPI()
        lang_pages = {}
        for pageid in pageids:
            data = self.pages.search("title,language",
                                     {"id":pageid,"pending":1})
            if len(data) == 0:
                continue
            title,lang = data[0]
            if lang in lang_pages:
                lang_pages[lang].append(title)
            else:
                lang_pages[lang] = [title]
        failed_titles = []
        for lang in lang_pages:
            titles = lang_pages[lang]
            htmls = api.get_contents(titles,lang)
            raw_texts = list(map(api.extract,htmls))
            for i in range(len(titles)):
                title = titles[i]
                if raw_texts[i] == "":
                    failed_titles.append(title)
                    self.pages.update({"error":1,"pending":0},{"title":title,"language":lang})
                    continue
                count_dict = api.wordcount(raw_texts[i])
                for word in count_dict:
                    count = count_dict[word]
                    self.register(word,title,count,lang)
                self.pages.update({"downloaded":1,"pending":0,"error":0},{"title":title,"language":lang})
        return failed_titles

#HTML
def make_row(vs,style = 'align="center"'):
    row_list = [f'<td {style}>{v}</td>' for v in vs]
    return "<tr>"+"".join(row_list)+"</tr>"

def make_table(datas,titles= []):
    table_html = '<table border="2">'
    if len(titles) > 0:
        table_html += make_row(titles,
                               'style="font-weight: bold;" align="center"')
    for data in datas:
        table_html += make_row(data)
    table_html += "</table>"
    return table_html
