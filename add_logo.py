import PIL
import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from icrawler.builtin import GoogleImageCrawler, ImageDownloader
from urllib.parse import urlparse

size_220_124 = (220, 124)
size_260_360 = (260, 360)
size_480_320 = (480, 320)

folder_cache = os.path.join(os.path.dirname(__file__), "cache")
folder_storage  = os.path.join(os.path.dirname(__file__), "storage")
logo = Image.open(os.path.join(os.path.dirname(__file__), "55.PNG"))
r,g,b,a = logo.split()

def resize_image(img, size):
    img = img.resize(size, Image.ANTIALIAS)
    return img

def generate_image(file_path, name, portrait, ratings):
    img = Image.open(file_path)
    if portrait:
        size = size_260_360
    else:
        size = size_220_124
    new_img = resize_image(img, size)
    new_img.paste(logo, (0, 0), mask = a)
    new_img.save(os.path.join(folder_storage, name + ("-260x360" if portrait else "-220x124") + '.jpg'))
    if ratings >= 7.8 and not portrait:
        new_img = resize_image(img, size_480_320)
        new_img.paste(logo, (0, 0), mask = a)
        new_img.save(os.path.join(folder_storage, name + "-480x320" + '.jpg'))

def crawl_image(name, portrait, ratings):
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
                                   downloader_cls=MyImageDownloader)
    portrait_mode = "海报" if portrait else "壁纸"

    google_crawler.crawl(keyword=name+"+电影+"+portrait_mode, max_num=1)
    # filename = name + ("-竖屏" if portrait else "-横屏")
    abspath = os.path.join(folder_cache, filename)
    generate_image(abspath, name, portrait, ratings)

def auto_fetch_and_resize(name, ratings):
    crawl_image(name, True, ratings)
    crawl_image(name, False, ratings)
