import config
from review_filter import ReviewFilter
from review_parser import SteamReviewsParser

if __name__ == "__main__":
    rf = ReviewFilter(min_chars=40, min_words=6, require_cyrillic=True, cyrillic_ratio=0.25)

    parser = SteamReviewsParser(
        base_url=config.BASE_URL,
        user_agent=config.USER_AGENT,
        sleep_seconds=0.3,
        review_filter=rf
    )

    parser.save_csv(
        path="stardew_reviews.csv",
        total_count=100_000,
        language="russian",
        flt="all",
        only_steam_purchase=True
    )
