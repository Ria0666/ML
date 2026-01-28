from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GroupSpec:
    group: str
    roots: List[str]
    max_depth: int = 2
    max_images: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
