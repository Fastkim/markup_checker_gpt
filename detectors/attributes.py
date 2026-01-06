import re
from collections import Counter

TAG_OPEN_REGEX = re.compile(r"<\s*([a-zA-Z0-9:-]+)\s+([^>]*?)>", re.DOTALL)
ATTR_REGEX = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=')

def check_duplicate_attributes(html: str, index_to_linecol):
    errors = []

    for m in TAG_OPEN_REGEX.finditer(html):
        tag = m.group(1).lower()
        attr_text = m.group(2)
        start_idx = m.start()

        attrs = [a.lower() for a in ATTR_REGEX.findall(attr_text)]
        if not attrs:
            continue

        cnt = Counter(attrs)
        dups = [k for k, v in cnt.items() if v > 1]
        if dups:
            line, col = index_to_linecol(start_idx)
            errors.append({
                "type": "duplicate_attributes",
                "tag": tag,
                "line": line,
                "col": col,
                "detail": f"<{tag}> 요소에 중복 속성: {', '.join(dups)}",
                "index": start_idx
            })

    return errors