from bs4 import BeautifulSoup
from models import Book

class BookParser:
    @staticmethod
    def parse_books(page_content: str, page_num: int) -> list[Book]:
        if not page_content:
            return []
            
        soup = BeautifulSoup(page_content, 'html.parser')
        books = []

        book_cards = soup.find_all('div', class_='product-card')
        
        print(f"Страница {page_num}: найдено {len(book_cards)} книг")

        for book_html in book_cards:
            book = Book.from_html(book_html)
            if book:
                books.append(book)
        
        return books
