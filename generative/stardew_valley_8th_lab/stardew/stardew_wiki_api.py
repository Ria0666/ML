import time
from typing import Dict, Iterable, List, Optional

import requests


RETRYABLE_STATUS = {429, 502, 503, 504}


class WikiAPI:
    def __init__(self, api_url: str, user_agent: str, max_retries: int = 8):
        self.api_url = api_url
        self.user_agent = user_agent
        self.max_retries = max_retries
        self._reset_session()

    def _reset_session(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": self.user_agent, "Connection": "close"})

    def get_json(self, params: Dict) -> Dict:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                r = self.s.get(self.api_url, params=params, timeout=30)
                if r.status_code in RETRYABLE_STATUS:
                    time.sleep(min(20.0, 2 ** attempt))
                    continue
                r.raise_for_status()
                return r.json()
            except (requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                last_err = e
                time.sleep(min(20.0, 2 ** attempt))
                try:
                    self.s.close()
                except Exception:
                    pass
                self._reset_session()
        raise RuntimeError(f"WikiAPI failed after retries: {last_err}")

    def iter_category_members(self, category_title: str) -> Iterable[Dict]:
        cmcontinue = None
        while True:
            params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": category_title,
                "cmlimit": "500",
                "cmtype": "file|subcat",
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            data = self.get_json(params)
            for item in data.get("query", {}).get("categorymembers", []):
                yield item

            cmcontinue = data.get("continue", {}).get("cmcontinue")
            if not cmcontinue:
                return

    def imageinfo_batch(self, titles: List[str], batch_size: int = 50) -> Dict[str, Dict]:
        out: Dict[str, Dict] = {}
        for i in range(0, len(titles), batch_size):
            chunk = titles[i:i + batch_size]
            params = {
                "action": "query",
                "format": "json",
                "titles": "|".join(chunk),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
            }
            data = self.get_json(params)
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                title = page.get("title")
                ii = page.get("imageinfo") or []
                if title and ii:
                    out[title] = ii[0]
        return out
