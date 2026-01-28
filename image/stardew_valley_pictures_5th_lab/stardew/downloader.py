import os
import time
from typing import Optional

import requests


RETRYABLE_STATUS = {429, 502, 503, 504}


def download_with_retries(url: str, out_path: str, user_agent: str, max_retries: int = 8) -> str:
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

                tmp = out_path + ".part"
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            f.write(chunk)

                os.replace(tmp, out_path)
                return out_path

        except (requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_err = e
            time.sleep(min(20.0, 2 ** attempt))
        except Exception as e:
            last_err = e
            time.sleep(min(10.0, 2 ** attempt))

    raise RuntimeError(f"Download failed after retries: {last_err}")
