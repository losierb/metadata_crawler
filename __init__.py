from extract_info import getmovieinfo

if __name__ == "__main__":
    while True:
        filename = input("输入电影文件名：")
        try:
            if filename == 'quit':
                exit(0)
            else:
                getmovieinfo(filename)
        except:
            pass