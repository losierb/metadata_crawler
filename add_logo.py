import PIL
import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from icrawler.builtin import GoogleImageCrawler, ImageDownloader
import logging
from urllib.parse import urlparse



folder_cache = os.path.join(os.path.dirname(__file__), "cache")
folder_storage  = os.path.join(os.path.dirname(__file__), "storage")
logo = Image.open(os.path.join(os.path.dirname(__file__), "55.PNG"))
r,g,b,a = logo.split()

if not os.path.isdir(folder_storage):
    os.mkdir(folder_storage)

def resize_image(img, size):
    img = img.resize(size, Image.ANTIALIAS)
    return img

def generate_image(name, size):
    """ str, str, (int, int) -> str """
    width, height = size
    potrait = ''
    if width > height:
        potrait = "-横屏"
    else:
        potrait = "-竖屏"
    file_path = os.path.join(folder_cache, name + potrait)
    img = Image.open(file_path)
    path = os.path.join(folder_storage, name + "-{0}x{1}".format(width, height) + '.jpg')
    new_img = resize_image(img, size)
    new_img.paste(logo, (0, 0), mask = a)
    new_img.save(path)
    return path

def crawl_image(name, portrait):
    filename = name + ("-竖屏" if portrait else "-横屏")
    class MyImageDownloader(ImageDownloader):
        def get_filename(self, task, default_ext):
            url_path = urlparse(task['file_url'])[2]
            if '.' in url_path:
                extension = url_path.split('.')[-1]
                if extension.lower() not in [
                        'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif', 'ppm', 'pgm'
                ]:
                    extension = default_ext
            else:
                extension = default_ext
            full_name = filename
            #full_name = '{}.{}'.format(filename, extension)
            return full_name

    google_storage = {'root_dir': folder_cache}
    google_crawler = GoogleImageCrawler(parser_threads=1, 
                                   downloader_threads=1, 
                                   storage=google_storage,
                                   downloader_cls=MyImageDownloader,
                                   log_level=logging.ERROR)
    portrait_mode = "海报" if portrait else "剧照"

    google_crawler.crawl(keyword=name+"+电影+"+portrait_mode, max_num=1)

def auto_fetch_image(name):
    crawl_image(name, True)
    crawl_image(name, False)
