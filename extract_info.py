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

def get_video_info(fileId, name):
    is_tv_series = False
    regex = re.compile(r'^(.+)-(.+?语).+\..+$')
    pat = regex.match(name)

    if pat == None:
        raise Exception("File name not recognized")

    video_name = pat.group(1)
    lang = pat.group(2)

    if re.match(r'(.*)第([0-9]+)集', video_name) != None:
        is_tv_series = True
        #raise "这是电视剧"
    if is_tv_series:
        pat = re.match(r'(.*)第([0-9]+)集', video_name)
        tv_series_name = pat.group(1)
        tv_series_number = int(pat.group(2))
        add_tv_series(fileId, tv_series_name, tv_series_number, lang)
    else:
        add_movie(fileId, video_name, lang)
    #data = urllib.urlencode(values)

def add_tv_series(fileId, tv_series_name, tv_series_number, lang):
    # first, check if they have already filled the existed name
    try:
        pid = server_interact.query_tv_series_id(tv_series_name)
        fill_info = {
            "action": "video",
            "fileId": fileId,
            "title": tv_series_name,
            "pid": pid,
            "type": "video",
            "episode": tv_series_number,
            "watermark":2
        }
        server_interact.upload_tv_series_info(fill_info, pid)
    except:
        print("tv series {0} not registed, doing it now!".format(tv_series_name))
        searchurl = douban_search_url + urllib.parse.quote(tv_series_name)
        result = getjson(searchurl)
        if result['count'] == 0 or len(result['subjects']) == 0:
            searchurl = douban_search_url + urllib.parse.quote(tv_series_name)
            result = getjson(searchurl)
            if result['count'] == 0 or len(result['subjects']) == 0:
                raise Exception("no such tv series found")
        else:
            id = -1
            for i in result['subjects']:
                if i['subtype'] == "tv":
                    id = i['id']
            if id == -1:
                raise Exception("No such tv series found")
            url = douban_info_url + id
            r = getjson(url)
            if r['subtype'] != 'tv':
                raise Exception("Not a tv!")
            add_logo.auto_fetch_image(r['title'], False)

            summary = r['summary'].replace("©豆瓣","")
            if(len(summary) > 255):
                summary = trim_last(summary[:255], '。') + '。'

            fill_info = {
                "action":"box",
                "title": tv_series_name,
                "type":"box",
                "area": util.find_area_id(r['countries'][0], util.tv_series_id),
                "director": [server_interact.query_people_id(x['name']) for x in r['directors']],
                "actor":[server_interact.query_people_id(x['name']) for x in r['casts']],
                "channel": util.tv_series_id,
                "language": util.find_language_id(lang, util.tv_series_id),
                "premiere":str(r['year']),
                "dbRating": r['rating']['average'],
                "subtitle": '' if len(r['aka']) == 0 else r['aka'][0],
                "totalEpisode": r['episodes_count'],
                "description": summary,
                "viewTall": generate_and_upload(r['title'], size_260_360),
                "viewFat": generate_and_upload(r['title'], size_220_124),
                "watermark":2
            }
            if(r['rating']['average'] >= 7.8):
                fill_info['viewTopic'] = generate_and_upload(r['title'], size_480_320)
            server_interact.upload_movie_info(fill_info)
            add_tv_series(fileId, tv_series_name, tv_series_number, lang)

def add_movie(fileId, movie_name, lang):
    searchurl = douban_search_url + urllib.parse.quote(movie_name)
    #content = urllib.request.unquote(response.read())  #得到
    result = getjson(searchurl)

    if result['count'] == 0 or len(result['subjects']) == 0:
        movie_name = trim_last(movie_name, '（')
        searchurl = douban_search_url + urllib.parse.quote(movie_name)
        result = getjson(searchurl)
        if result['count'] == 0 or len(result['subjects']) == 0:
            raise Exception("No such movie found")
    else:
        id = -1
        for i in result['subjects']:
            if i['subtype'] == "movie":
                id = i['id']
        if id == -1:
            raise Exception("No such movie found")
        url = douban_info_url + id
        r = getjson(url)
        if r['subtype'] != 'movie':
            raise Exception("Not a movie!")
        add_logo.auto_fetch_image(r['title'], True)

        summary = r['summary'].replace("©豆瓣","")
        if(len(summary) > 255):
            summary = trim_last(summary[:255], '。') + '。'
        fill_info = {
            "action": "video",
            "fileId": fileId,
            "title": r['title'],
            "subtitle": '' if len(r['aka']) == 0 else r['aka'][0],
            "type":"video",
            "style":[util.find_style_id(x, util.movie_id) for x in r['genres']],
            "area": util.find_area_id(r['countries'][0], util.movie_id),
            "director":[server_interact.query_people_id(x['name']) for x in r['directors']],
            "actor":[server_interact.query_people_id(x['name']) for x in r['casts']],
            "channel":14,
            "language": util.find_language_id(lang, util.movie_id),
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
        server_interact.upload_movie_info(fill_info)