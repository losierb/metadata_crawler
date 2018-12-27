import urllib.request
import sqlite3
import re
import json
import add_logo

fields = ["title", "genres", "rating", "casts"]

douban_search_url = 'http://api.douban.com/v2/movie/search?q='
douban_info_url = 'https://api.douban.com/v2/movie/subject/'

def getjson(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf8'))

def normalize_language(lang):
    if(lang == "国语"):
        return "普通话"
    else:
        return lang

def getmovieinfo(values):
    regex = re.compile(r'^(.+)-(.+?)[0-9]+P\..+$')
    pat = regex.match(values)
    if(pat == None):
        raise "文件名不匹配"
    movie_name = pat.group(1)
    lang = pat.group(2)
    #data = urllib.urlencode(values)
    searchurl = douban_search_url + urllib.parse.quote(movie_name)

    #content = urllib.request.unquote(response.read())  #得到
    result = getjson(searchurl)

    if result['count'] == 0:
        raise "no such movie found"
    else:
        id = result['subjects'][0]['id']
        url = douban_info_url + id
        r = getjson(url)
        add_logo.auto_fetch_and_resize(r['title'], r['rating']['average'])
        print("片名: " + r['title'])
        print("别名: " + ', '.join(x for x in r['aka']))
        print("评分: " + str(r['rating']['average']))
        print("年份: " + r['year'])
        print("语言：" + normalize_language(lang))
        print("风格: " + ', '.join(x for x in r['genres']))
        print("国家: " + ', '.join(x for x in r['countries']))
        print("导演: " + ', '.join(x['name'] for x in r['directors']))
        print("演员: " + ', '.join(x['name'] for x in r['casts']))
        summary = r['summary'].replace(".©豆瓣","")
        if(len(summary) > 255):
            summary = summary[:252]+"……"
        print("简介: " + summary)
