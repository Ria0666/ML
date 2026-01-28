import os
import csv
from typing import Dict, List, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

from .types import GroupSpec
from .utils import ensure_dirs, sha1, guess_ext
from .downloader import download_with_retries
from .stardew_wiki_api import WikiAPI

META_FIELDS = ["group", "image_path", "source_category", "file_title", "url", "mime", "width", "height", "bytes"]


def collect_file_titles(api: WikiAPI, spec: GroupSpec) -> List[Tuple[str, str]]:
    seen: Set[str] = set()
    queue: List[Tuple[str, int]] = [(c, 0) for c in spec.roots]
    out: List[Tuple[str, str]] = []

    while queue:
        cat, depth = queue.pop(0)
        if cat in seen:
            continue
        seen.add(cat)

        for item in api.iter_category_members(cat):
            ns = item.get("ns")
            title = item.get("title", "")

            if ns == 14 and depth < spec.max_depth:
                queue.append((title, depth + 1))
                continue

            if ns == 6 and title.startswith("File:"):
                out.append((cat, title))
                if spec.max_images is not None and len(out) >= spec.max_images:
                    return out

    return out


def pass_size_filter(spec: GroupSpec, info: Dict) -> bool:
    w = info.get("width")
    h = info.get("height")
    if spec.min_width is not None and w is not None and w < spec.min_width:
        return False
    if spec.min_height is not None and h is not None and h < spec.min_height:
        return False
    return True


def write_row(writer: csv.DictWriter, row: Dict) -> None:
    writer.writerow(row)


def flush_futures(writer: csv.DictWriter, future_map: Dict) -> int:
    wrote = 0
    for fut in as_completed(list(future_map.keys())):
        row = future_map.pop(fut)
        row["image_path"] = fut.result()
        write_row(writer, row)
        wrote += 1
    return wrote


def schedule_one_download(
    ex: ThreadPoolExecutor,
    future_map: Dict,
    row: Dict,
    url: str,
    img_path: str,
    user_agent: str,
    max_retries: int,
) -> None:
    fut = ex.submit(download_with_retries, url, img_path, user_agent, max_retries)
    future_map[fut] = row


def build_group(
    api: WikiAPI,
    ex: ThreadPoolExecutor,
    writer: csv.DictWriter,
    future_map: Dict,
    spec: GroupSpec,
    images_root: str,
    global_seen_files: Set[str],
    batch_size: int,
    queue_limit: int,
    user_agent: str,
    max_retries: int,
) -> int:
    group_dir = os.path.join(images_root, spec.group)
    ensure_dirs(group_dir)

    candidates = collect_file_titles(api, spec)

    filtered: List[Tuple[str, str]] = []
    for cat, ft in candidates:
        if ft in global_seen_files:
            continue
        global_seen_files.add(ft)
        filtered.append((cat, ft))

    print(f"== {spec.group} | files: {len(filtered)} ==")

    total = 0
    for i in range(0, len(filtered), batch_size):
        chunk = filtered[i:i + batch_size]
        titles = [ft for _, ft in chunk]
        infos = api.imageinfo_batch(titles, batch_size=batch_size)

        for cat, ft in chunk:
            info = infos.get(ft)
            if not info:
                continue
            if not pass_size_filter(spec, info):
                continue

            url = info.get("url")
            if not url:
                continue

            mime = info.get("mime")
            ext = guess_ext(url, mime)
            img_path = os.path.join(group_dir, f"{sha1(url)}{ext}")

            row = {
                "group": spec.group,
                "image_path": "",
                "source_category": cat,
                "file_title": ft,
                "url": url,
                "mime": mime,
                "width": info.get("width"),
                "height": info.get("height"),
                "bytes": info.get("size"),
            }

            if os.path.exists(img_path):
                row["image_path"] = img_path
                write_row(writer, row)
                total += 1
            else:
                schedule_one_download(ex, future_map, row, url, img_path, user_agent, max_retries)

            if len(future_map) >= queue_limit:
                total += flush_futures(writer, future_map)

    total += flush_futures(writer, future_map)
    print(f"[{spec.group}] done. rows written: {total}")
    return total


def build_dataset(
    api: WikiAPI,
    groups: List[GroupSpec],
    out_dir: str,
    images_root: str,
    meta_csv: str,
    user_agent: str,
    max_workers: int,
    batch_size: int,
    queue_limit: int,
    max_retries: int,
) -> None:
    ensure_dirs(out_dir, images_root)

    global_seen_files: Set[str] = set()
    total_rows = 0

    with open(meta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=META_FIELDS)
        writer.writeheader()

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            future_map: Dict = {}

            for spec in groups:
                total_rows += build_group(
                    api=api,
                    ex=ex,
                    writer=writer,
                    future_map=future_map,
                    spec=spec,
                    images_root=images_root,
                    global_seen_files=global_seen_files,
                    batch_size=batch_size,
                    queue_limit=queue_limit,
                    user_agent=user_agent,
                    max_retries=max_retries,
                )

    print("DONE")
    print("Images root:", images_root)
    print("Metadata:", meta_csv)
    print("Rows:", total_rows)