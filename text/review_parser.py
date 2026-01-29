import csv
import time
import requests

class SteamReviewsParser:
    def __init__(self, base_url: str, user_agent: str, sleep_seconds: float, review_filter):
        self.base_url = base_url
        self.sleep_seconds = sleep_seconds
        self.review_filter = review_filter

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def iter_reviews(self, total_count=100_000, language="russian", flt="all", only_steam_purchase=True):
        cursor = "*"
        got = 0

        while got < total_count:
            params = {
                "json": 1,
                "num_per_page": 100,
                "cursor": cursor,
                "language": language,
                "filter": flt,
                "review_type": "all",
                "purchase_type": "all",
            }

            r = self.session.get(self.base_url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            reviews = data.get("reviews", [])
            if not reviews:
                break

            for rev in reviews:
                steam_purchase = rev.get("steam_purchase", False)
                if only_steam_purchase and not steam_purchase:
                    continue

                text = (rev.get("review") or "").strip()
                if not self.review_filter.accept(text, language=language):
                    continue

                author = rev.get("author", {}) or {}
                playtime_minutes = author.get("playtime_forever")

                yield {
                    "review_id": rev.get("recommendationid"),
                    "review_text": text,
                    "voted_up": rev.get("voted_up"),
                    "steam_purchase": steam_purchase,
                    "playtime_hours": (playtime_minutes / 60.0) if playtime_minutes is not None else None,
                    "likes": rev.get("votes_up"),
                    "funny_votes": rev.get("votes_funny"),
                    "weighted_vote_score": rev.get("weighted_vote_score"),
                    "language": rev.get("language"),
                }

                got += 1
                if got >= total_count:
                    break

            prev_cursor = cursor
            cursor = data.get("cursor", cursor)
            if cursor == prev_cursor:
                break

            time.sleep(self.sleep_seconds)

    def save_csv(self, path="stardew_reviews.csv", total_count=100_000, language="russian",
                 flt="all", only_steam_purchase=True):
        fieldnames = [
            "review_id","review_text","voted_up","steam_purchase",
            "playtime_hours","likes","funny_votes","weighted_vote_score","language"
        ]

        saved = 0
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in self.iter_reviews(total_count, language, flt, only_steam_purchase):
                writer.writerow(row)
                saved += 1
                if saved % 1000 == 0:
                    print("Saved:", saved)

        print("Done. Rows:", saved)