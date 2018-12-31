from extract_info import get_video_info
from server_interact import fetch_next_program
if __name__ == "__main__":
    page = 1
    while True:
        ret = fetch_next_program(get_video_info, page)
        if ret == False:
            page = page + 1
