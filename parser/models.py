from dataclasses import dataclass
import re

@dataclass
class Book:
    title: str
    price: float
    old_price: float
    discount_percent: int
    publisher: str
    category: str
    availability: str
    target: float

    @classmethod
    def from_html(cls, book_html):
        try:
            title = book_html.get('data-product-name', '')
            if not title:
                img = book_html.find('img')
                if img:
                    title = img.get('alt', '')

            price = 0.0
            old_price = 0.0
            discount_percent = 0

            price_discounted = book_html.get('data-product-price-discounted')
            price_total = book_html.get('data-product-price-total')
            
            if price_discounted:
                price = float(price_discounted)
            if price_total:
                old_price = float(price_total)

            if price == 0:
                price_info = book_html.find('div', class_='price-info')
                if price_info:
                    current_price_elem = price_info.find('span', class_='price-info__price')
                    if current_price_elem:
                        price_text = current_price_elem.get_text(strip=True)
                        price_match = re.search(r'[\d\s]+', price_text.replace('₽', '').replace(' ', ''))
                        if price_match:
                            price = float(price_match.group())
                    
                    old_price_elem = price_info.find('span', class_='price-info__old-price')
                    if old_price_elem:
                        old_price_text = old_price_elem.get_text(strip=True)
                        old_price_match = re.search(r'[\d\s]+', old_price_text.replace('₽', '').replace(' ', ''))
                        if old_price_match:
                            old_price = float(old_price_match.group())

            if old_price > 0 and price > 0:
                discount_percent = int(((old_price - price) / old_price) * 100)

            publisher = book_html.get('data-product-brand', 'Неизвестно')

            category = book_html.get('data-product-category', 'Книги')
            if category and '|||' in category:
                category = category.split('|||')[0]

            availability = book_html.get('data-product-status', 'В наличии')
            if not availability or availability == '1':
                availability = 'В наличии'

            target = price

            return cls(title, price, old_price, discount_percent, publisher, 
                      category, availability, target)

        except Exception as e:
            print(f"Ошибка при создании объекта книги: {e}")
            return None
