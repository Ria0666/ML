import pandas as pd
from models import Book
from config import OUTPUT_CSV


class DataProcessor:
    @staticmethod
    def save_to_csv(books: list[Book], filename: str = OUTPUT_CSV) -> None:
        if books:
            data = [book.__dict__ for book in books]
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Данные сохранены в {filename}")
            print(f"Размер датасета: {len(df)} строк, {len(df.columns)} столбцов")
        else:
            print("Нет данных для сохранения")

