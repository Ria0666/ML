API_URL = "https://stardewvalleywiki.com/mediawiki/api.php"
USER_AGENT = "Mozilla/5.0 (compatible; StardewGenDataset/1.0)"

OUT_DIR = "dataset"
IMAGES_DIR = f"{OUT_DIR}/images_48"
META_CSV = f"{OUT_DIR}/metadata.csv"

MAX_WORKERS = 8
MAX_RETRIES = 8
IMAGEINFO_BATCH_SIZE = 50
DOWNLOAD_QUEUE_LIMIT = 300
TARGET_SIZE = 48
MAX_ORIG_WIDTH = 600
MAX_ORIG_HEIGHT = 600
MAX_IMAGES_TOTAL = 50000
CATEGORIES = [
    "Category:Springobjects images",
    "Category:Craftable item images",
    "Category:Furniture images",
    "Category:Fish images",
    "Category:Weapon images",
    "Category:Monster images",
    "Category:Seed images",
    "Category:Crop images",
    "Category:Sapling images",
]

MAX_DEPTH = 3
