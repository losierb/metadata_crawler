import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import json
import random
import os
import mimetypes
import server_interact
import traceback

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

auth = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyUm9sZXMiOiJST0xFX0FETUlOIiwiZXhwIjoxNTQ2Mzk0OTI3LCJ1c2VySWQiOjEsImFjY291bnQiOiJhZG1pbiJ9.v4kuwiEjZ3hndr_q7bWeYZnwMU_J8oaDheAmS8V9sl2pAC33JEIK8wKhiAZ0Og2F7MjpJIljUNZRBy1mtrCI-g'

cjar=http.cookiejar.CookieJar()
cookie=urllib.request.HTTPCookieProcessor(cjar)
opener=urllib.request.build_opener(cookie)
urllib.request.install_opener(opener)

#base_url = 'http://104.25.24.99'
base_url = 'http://a.mm6.com'

def get_from_server(url):
    myheaders = {
            #'Host': 'a.mm6.com',
            'Connection': ' keep-alive',
            'Accept': 'application/manage+json',
            'Authentication': auth,
            'User-Agent': user_agent,
            'Origin': 'http://b.mm6.com',
            'Referer': 'http://b.mm6.com/video/adminfiles',
            'Content-Type': 'application/json;charset=utf-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }
    request = urllib.request.Request(url, headers=myheaders, method="GET")
    response=urllib.request.urlopen(request)
    return json.loads(response.read())

def query_people_id(actor_name):
    get_url = base_url + "/api/v2/actor?name=" + urllib.parse.quote(actor_name)
    ret = get_from_server(get_url)
    for record in ret['rows']:
        if record['name'] == actor_name:
            return record['id']
    post_actor(actor_name)
    return query_people_id(actor_name)

def query_tv_series_id(tv_series_name):
    get_url = base_url + "/api/v2/video?title=" + urllib.parse.quote(tv_series_name)
    ret = get_from_server(get_url)
    for record in ret['rows']:
        if record['title'] == tv_series_name:
            return record['id']
    raise Exception("tv series id not found!")

def post_to_server(keypair, post_url):
    myheaders = {
            #'Host': 'a.mm6.com',
            'Connection': ' keep-alive',
            'Accept': 'application/manage+json',
            'Authentication': auth,
            'User-Agent': user_agent,
            'Origin': 'http://b.mm6.com',
            'Referer': 'http://b.mm6.com/video/adminfiles',
            'Content-Type': 'application/json;charset=utf-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }
    mymethod = "POST"
    mydata = json.dumps(keypair, ensure_ascii=False).encode('utf8')
    myheaders['Content-Length'] = len(mydata)
    request = urllib.request.Request(post_url, data=mydata, headers=myheaders, method=mymethod)
    try:
        urllib.request.urlopen(request)
        return True
    except urllib.error.HTTPError:
        return False

def post_actor(name):
    post_url = base_url + '/api/v2/actor'
    actor = {"name":name}
    post_to_server(actor, post_url)

def post_picture(path):
    filename = os.path.basename(path)
    boundary = "----WebKitFormBoundary1RF3Ams6ESFqc7K6"
    picture_upload_url = "http://s.mm6.com/api/v2/file"
    myheaders = {
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Authentication': auth,
            'User-Agent': user_agent,
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'http://b.mm6.com',
            'Referer': 'http://b.mm6.com/video/adminfiles',
            'Content-Type': 'multipart/form-data; boundary=' + boundary,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        }
    def escape_quote(s):
        return s.replace('"', '\\"')

    fp = open(path, 'rb')

    lines = []

    lines.extend((
        '--{0}'.format(boundary).encode('utf8'),
        b'Content-Disposition: form-data; name="type"',
        b'',
        b'image',
    ))

    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    lines.extend((
        '--{0}'.format(boundary).encode('utf8'),
        'Content-Disposition: form-data; name="file"; filename="{0}"'.format(escape_quote(filename)).encode('utf8'),
        'Content-Type: {0}'.format(mimetype).encode('utf8'),
        b'',
        fp.read()
    ))

    lines.extend((
        '--{0}--'.format(boundary).encode('utf8'),
        b'',
    ))
    body = b'\r\n'.join(lines)

    myheaders['Content-Length'] = str(len(body))

    mymethod = "POST"
    request = urllib.request.Request(picture_upload_url, data=body, headers=myheaders, method=mymethod)
    try:
        response=urllib.request.urlopen(request)
        return response.read().decode('utf8')
    except urllib.error.HTTPError:
        raise Exception("Upload failed")

def upload_movie_info(form):
    post_url = base_url + "/api/v2/video"
    post_to_server(form, post_url)

def upload_tv_series_info(form, pid):
    post_url = base_url + "/api/v2/video/" + pid
    post_to_server(form, post_url)

def fetch_next_program(f, page):
    get_url = base_url + "/api/v2/source?ps=10&pn={0}&status=1".format(page)
    ret = get_from_server(get_url)
    for item in ret['rows']:
        try:
            f(item['fileId'], item['name'])
        except Exception as e:
            print("failed adding {0}: {1}".format(item['name'], e))
