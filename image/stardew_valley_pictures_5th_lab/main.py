import config
from stardew.types import GroupSpec
from stardew.stardew_wiki_api import WikiAPI
from stardew.dataset_builder import build_dataset


def main():
    api = WikiAPI(config.API_URL, config.USER_AGENT, max_retries=config.MAX_RETRIES)

    groups = []
    for g in config.GROUPS:
        groups.append(GroupSpec(
            group=g["group"],
            roots=g["roots"],
            max_depth=g.get("max_depth", 2),
            max_images=config.MAX_IMAGES_PER_CLASS,
            min_width=config.MIN_WIDTH,
            min_height=config.MIN_HEIGHT,
        ))

    build_dataset(
        api=api,
        groups=groups,
        out_dir=config.OUT_DIR,
        images_root=config.IMAGES_ROOT,
        meta_csv=config.META_CSV,
        user_agent=config.USER_AGENT,
        max_workers=config.MAX_WORKERS,
        batch_size=config.IMAGEINFO_BATCH_SIZE,
        queue_limit=config.DOWNLOAD_QUEUE_LIMIT,
        max_retries=config.MAX_RETRIES,
    )


if __name__ == "__main__":
    main()
