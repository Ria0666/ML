import re
from dataclasses import dataclass

@dataclass
class ReviewFilter:
    min_chars: int = 40
    min_words: int = 6
    require_cyrillic: bool = True
    cyrillic_ratio: float = 0.25

    def accept(self, text: str, language: str) -> bool:
        if not text:
            return False
        t = text.strip()

        if len(t) < self.min_chars:
            return False

        if not re.search(r"[A-Za-zА-Яа-яЁё0-9]", t):
            return False

        words = re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", t)
        if len(words) < self.min_words:
            return False

        if self.require_cyrillic and language == "russian":
            letters = [ch for ch in t if ch.isalpha()]
            if not letters:
                return False
            cyr = sum(("а" <= ch.lower() <= "я") or (ch.lower() == "ё") for ch in letters)
            if (cyr / len(letters)) < self.cyrillic_ratio:
                return False

        return True
