import urllib.request
import sqlite3
import re
import json
import add_logo
import server_interact
import util

fields = ["title", "genres", "rating", "casts"]

douban_search_url = 'http://api.douban.com/v2/movie/search?q='
douban_info_url = 'https://api.douban.com/v2/movie/subject/'

size_220_124 = (220, 124)
size_260_360 = (260, 360)
size_480_320 = (480, 320)

def trim_last(s: str, l: str) -> str:
    return s[:s.rfind(l)]

def getjson(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf8'))

def generate_and_upload(name, size):
    output_path = add_logo.generate_image(name, size)
    image_id = server_interact.post_picture(output_path)
    return image_id

def getmovieinfo(fileId, name):
    print("in getmovieinfo({0}, {1})".format(fileId, name))
    regex = re.compile(r'^(.+)-(.+?)[0-9]+P\..+$')
    pat = regex.match(name)
    if pat == None:
        raise "文件名不匹配"
    if re.match(".*第([0-9]+)集", name) != None:
        raise "这是电视剧"
    movie_name = pat.group(1)
    lang = pat.group(2)
    #data = urllib.urlencode(values)
    searchurl = douban_search_url + urllib.parse.quote(movie_name)

    #content = urllib.request.unquote(response.read())  #得到
    result = getjson(searchurl)

    if result['count'] == 0 or len(result['subjects']) == 0:
        substring = trim_last(movie_name, '（')
        searchurl = douban_search_url + urllib.parse.quote(movie_name)
        result = getjson(searchurl)
        if result['count'] == 0 or len(result['subjects']) == 0:
            raise "no such movie found"
    else:
        id = result['subjects'][0]['id']
        url = douban_info_url + id
        r = getjson(url)
        if r['subtype'] != 'movie':
            raise "Not a movie!"
        add_logo.auto_fetch_image(r['title'])

        summary = r['summary'].replace("©豆瓣","")
        if(len(summary) > 255):
            summary = trim_last(summary[:255], '。') + '。'
        fill_info = {
            "action": "video",
            "fileId": fileId,
            "title": r['title'],
            "subtitle": '' if len(r['aka']) == 0 else r['aka'][0],
            "type":"video",
            "style":[util.find_style_id(x) for x in r['genres']],
            "area": util.find_area_id(r['countries'][0]),
            "director":[server_interact.query_people_id(x['name']) for x in r['directors']],
            "actor":[server_interact.query_people_id(x['name']) for x in r['casts']],
            "channel":14,
            "language": util.find_language_id(lang),
            "premiere":str(r['year']),
            "dbRating":r['rating']['average'],
            "description": summary,
            "viewTall": generate_and_upload(r['title'], size_260_360),
            "viewFat": generate_and_upload(r['title'], size_220_124),
            "watermark":2
        }
        if(r['rating']['average'] >= 7.8):
            fill_info['viewTopic'] = generate_and_upload(r['title'], size_480_320)
        #print(fill_info)
        server_interact.upload_info(fill_info)