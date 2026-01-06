import re
from collections import defaultdict

ID_ATTR_REGEX = re.compile(r'\bid\s*=\s*("([^"]+)"|\'([^\']+)\'|([^\s>]+))', re.IGNORECASE)

def check_duplicate_ids(html: str, index_to_linecol):
    id_positions = defaultdict(list)

    for m in ID_ATTR_REGEX.finditer(html):
        raw = m.group(2) or m.group(3) or m.group(4) or ""
        id_val = raw.strip()
        if not id_val:
            continue

        idx = m.start()
        line, col = index_to_linecol(idx)
        id_positions[id_val].append((line, col, idx))

    errors = []
    for id_val, pos_list in id_positions.items():
        if len(pos_list) > 1:
            errors.append({
                "type": "duplicate_id",
                "id": id_val,
                "count": len(pos_list),
                "positions": [{"line": l, "col": c, "index": i} for (l, c, i) in pos_list],
                "detail": f"id='{id_val}' 중복 사용 ({len(pos_list)}회)"
            })
    return errors