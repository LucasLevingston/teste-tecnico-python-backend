from typing import List, Optional


def normalize_tags(tags: Optional[List[str]]) -> Optional[str]:
    if not tags:
        return None
    return ",".join([t.strip() for t in tags if t and t.strip()])
