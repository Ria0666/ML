from crawler import BookCrawler
from parser import BookParser
from data_processor import DataProcessor
from config import PAGE_LIMIT


class MainProcess:
    def __init__(self):
        self.crawler = BookCrawler()
        self.parser = BookParser()
        self.processor = DataProcessor()

    def fetch_and_parse_page(self, page_num):
        url = self.crawler.get_page_url(page_num)
        page_content = self.crawler.fetch_page(url)

        if page_content:
            books = self.parser.parse_books(page_content, page_num)
            print(f"{url}")
            return books
        return []

    def crawl_site(self):
        all_books = []
        page_nums = range(1, PAGE_LIMIT + 1)

        for page_num in page_nums:
            books = self.fetch_and_parse_page(page_num)
            all_books.extend(books)

            print(f"Всего книг собрано: {len(all_books)}")

        return all_books

    def save_books(self, books):
        self.processor.save_to_csv(books)

def main():
    process = MainProcess()
    books = process.crawl_site()
    process.save_books(books)


if __name__ == '__main__':
    main()
