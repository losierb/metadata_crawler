from extract_info import getmovieinfo
from server_interact import fetch_next_program
if __name__ == "__main__":
    page = 0
    while True:
        fetch_next_program(getmovieinfo, page)
        page = page + 1
