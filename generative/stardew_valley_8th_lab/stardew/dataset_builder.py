import os
import csv
import re
from typing import Dict, List, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from .stardew_wiki_api import WikiAPI
from .downloader import download_and_process

META_FIELDS = [
    "image_path", "source_category", "file_title", "url",
    "orig_mime", "orig_width", "orig_height", "orig_bytes",
]

_DIALOGUE_RE = re.compile(r"(dialogue|textbox|conversation|ui|window|box|menu)", re.IGNORECASE)

ALLOWED_MIME = {"image/png", "image/jpeg", "image/webp", "image/gif"}


def collect_file_titles(api: WikiAPI, roots: List[str], max_depth: int) -> List[Tuple[str, str]]:
    seen = set()
    q = [(c, 0) for c in roots]
    out: List[Tuple[str, str]] = []

    while q:
        cat, depth = q.pop(0)
        if cat in seen:
            continue
        seen.add(cat)

        for item in api.iter_category_members(cat):
            ns = item.get("ns")
            title = item.get("title", "")

            if ns == 14 and depth < max_depth:
                q.append((title, depth + 1))
                continue

            if ns == 6 and title.startswith("File:"):
                out.append((cat, title))

    return out


def is_bad_for_generative(file_title: str, info: Dict, max_w: int, max_h: int) -> bool:
    w = info.get("width")
    h = info.get("height")
    mime = info.get("mime")

    if mime not in ALLOWED_MIME:
        return True

    if w and h:
        if (max_w and w > max_w) or (max_h and h > max_h):
            return True

        ratio = w / float(h)
        if w >= 600 and h <= 400 and ratio >= 2.2:
            return True

    if _DIALOGUE_RE.search(file_title):
        return True

    return False


def flush(writer: csv.DictWriter, futures: Dict) -> int:
    wrote = 0
    for fut in as_completed(list(futures.keys())):
        row = futures.pop(fut)
        row["image_path"] = fut.result()
        writer.writerow(row)
        wrote += 1
    return wrote


def build_generative_dataset(
    api: WikiAPI,
    categories: List[str],
    images_dir: str,
    meta_csv: str,
    user_agent: str,
    max_workers: int,
    batch_size: int,
    queue_limit: int,
    max_retries: int,
    target_size: int,
    max_depth: int,
    max_total: int,
    max_orig_w: int,
    max_orig_h: int,
) -> None:
    os.makedirs(images_dir, exist_ok=True)

    candidates = collect_file_titles(api, categories, max_depth=max_depth)

    seen_files: Set[str] = set()
    uniq: List[Tuple[str, str]] = []
    for cat, ft in candidates:
        if ft in seen_files:
            continue
        seen_files.add(ft)
        uniq.append((cat, ft))

    print("Candidates:", len(uniq))

    written = 0
    with open(meta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=META_FIELDS)
        writer.writeheader()

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures: Dict = {}

            for i in range(0, len(uniq), batch_size):
                chunk = uniq[i:i + batch_size]
                titles = [ft for _, ft in chunk]
                infos = api.imageinfo_batch(titles, batch_size=batch_size)

                for cat, ft in chunk:
                    info = infos.get(ft)
                    if not info:
                        continue

                    if is_bad_for_generative(ft, info, max_orig_w, max_orig_h):
                        continue

                    url = info.get("url")
                    if not url:
                        continue

                    out_path = os.path.join(images_dir, f"{hash(url)}.png")

                    row = {
                        "image_path": "",
                        "source_category": cat,
                        "file_title": ft,
                        "url": url,
                        "orig_mime": info.get("mime"),
                        "orig_width": info.get("width"),
                        "orig_height": info.get("height"),
                        "orig_bytes": info.get("size"),
                    }

                    if os.path.exists(out_path):
                        row["image_path"] = out_path
                        writer.writerow(row)
                        written += 1
                    else:
                        fut = ex.submit(download_and_process, url, out_path, user_agent, max_retries, target_size)
                        futures[fut] = row

                    if len(futures) >= queue_limit:
                        written += flush(writer, futures)
                        if max_total and written >= max_total:
                            break

                if max_total and written >= max_total:
                    break

            written += flush(writer, futures)

    print("DONE:", written)
    print("Images:", images_dir)
    print("Metadata:", meta_csv)