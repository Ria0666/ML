import requests
import time
import random
from config import HEADERS, MIN_DELAY, MAX_DELAY, BASE_URL
from multiprocessing import Pool

class BookCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def fetch_page(self, url: str) -> str:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка в скачивании страницы {url}: {e}")
            return None
    
    def get_page_url(self, page_num: int) -> str:
        if page_num == 1:
            return BASE_URL
        else:
            return f"{BASE_URL}?page={page_num}"


def fetch_page_parallel(page_num: int, crawler: BookCrawler):
    url = crawler.get_page_url(page_num)
    return crawler.fetch_page(url)

def fetch_all_pages_parallel(page_nums, crawler):
    with Pool(processes=4) as pool:
        results = pool.starmap(fetch_page_parallel, [(page_num, crawler) for page_num in page_nums])
    return results
