import os
import time
from typing import Optional

import requests
from PIL import Image, ImageOps

RETRYABLE_STATUS = {429, 502, 503, 504}


def _save_as_48px_png(src_path: str, dst_path: str, target_size: int) -> None:
    with Image.open(src_path) as im:
        if getattr(im, "is_animated", False):
            im.seek(0)

        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA")

        if im.mode == "RGBA":
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            bg.paste(im, mask=im.getchannel("A"))
            im = bg.convert("RGB")
        else:
            im = im.convert("RGB")

        im = ImageOps.pad(im, (target_size, target_size), method=Image.Resampling.LANCZOS, color=(255, 255, 255))
        im.save(dst_path, format="PNG", optimize=True)


def download_and_process(url: str, out_png_path: str, user_agent: str, max_retries: int, target_size: int) -> str:
    last_err: Optional[Exception] = None

    for attempt in range(max_retries):
        try:
            s = requests.Session()
            s.headers.update({"User-Agent": user_agent, "Connection": "close"})
            with s.get(url, stream=True, timeout=60) as r:
                if r.status_code in RETRYABLE_STATUS:
                    time.sleep(min(20.0, 2 ** attempt))
                    continue
                r.raise_for_status()

                tmp_raw = out_png_path + ".raw.part"
                tmp_png = out_png_path + ".png.part"

                with open(tmp_raw, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            f.write(chunk)

                _save_as_48px_png(tmp_raw, tmp_png, target_size)

                os.replace(tmp_png, out_png_path)
                try:
                    os.remove(tmp_raw)
                except OSError:
                    pass

                return out_png_path

        except (requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_err = e
            time.sleep(min(20.0, 2 ** attempt))
        except Exception as e:
            last_err = e
            time.sleep(min(10.0, 2 ** attempt))

    raise RuntimeError(f"Download failed after retries: {last_err}")
