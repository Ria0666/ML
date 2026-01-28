API_URL = "https://stardewvalleywiki.com/mediawiki/api.php"
USER_AGENT = "Mozilla/5.0 (compatible; StardewWikiImageParser/1.1)"
OUT_DIR = "dataset"
IMAGES_ROOT = f"{OUT_DIR}/images"
META_CSV = f"{OUT_DIR}/metadata.csv"
MAX_WORKERS = 8
MAX_RETRIES = 8
IMAGEINFO_BATCH_SIZE = 50
DOWNLOAD_QUEUE_LIMIT = 600
MIN_WIDTH = None
MIN_HEIGHT = None
MAX_IMAGES_PER_CLASS = 2000
GROUPS = [
    {"group": "characters", "roots": ["Category:NPC images"], "max_depth": 1},
    {"group": "fish", "roots": ["Category:Fish images"], "max_depth": 1},
    {"group": "plants", "roots": ["Category:Crop images", "Category:Seed images", "Category:Sapling images"], "max_depth": 2},
    {"group": "weapons", "roots": ["Category:Weapon images"], "max_depth": 2},
    {"group": "mobs", "roots": ["Category:Monster images"], "max_depth": 1},
    {"group": "features", "roots": ["Category:Features images"], "max_depth": 1},
]
