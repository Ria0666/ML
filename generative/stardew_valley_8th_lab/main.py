import config
from stardew.stardew_wiki_api import WikiAPI
from stardew.dataset_builder import build_generative_dataset


def main():
    api = WikiAPI(config.API_URL, config.USER_AGENT, max_retries=config.MAX_RETRIES)

    build_generative_dataset(
        api=api,
        categories=config.CATEGORIES,
        images_dir=config.IMAGES_DIR,
        meta_csv=config.META_CSV,
        user_agent=config.USER_AGENT,
        max_workers=config.MAX_WORKERS,
        batch_size=config.IMAGEINFO_BATCH_SIZE,
        queue_limit=config.DOWNLOAD_QUEUE_LIMIT,
        max_retries=config.MAX_RETRIES,
        target_size=config.TARGET_SIZE,
        max_depth=config.MAX_DEPTH,
        max_total=config.MAX_IMAGES_TOTAL,
        max_orig_w=config.MAX_ORIG_WIDTH,
        max_orig_h=config.MAX_ORIG_HEIGHT,
    )


if __name__ == "__main__":
    main()
