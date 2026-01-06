import re

TAG_REGEX = re.compile(r"<\s*(/)?\s*([a-zA-Z0-9:-]+)([^>]*)>", re.DOTALL)

SELF_CLOSING = {
    "area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"
}

def check_tag_structure(html: str, index_to_linecol):
    errors = []
    stack = []  # (tag, start_idx)

    for m in TAG_REGEX.finditer(html):
        full = m.group(0)
        is_close = bool(m.group(1))
        tag = (m.group(2) or "").lower()
        start_idx = m.start()

        # 주석/doctype 등 스킵 (간단 처리)
        if full.startswith("<!--") or tag in ("!doctype",):
            continue

        # self-closing 또는 <tag ... />
        is_self = tag in SELF_CLOSING or full.rstrip().endswith("/>")
        if is_self:
            continue

        if not is_close:
            stack.append((tag, start_idx))
        else:
            if not stack:
                line, col = index_to_linecol(start_idx)
                errors.append({
                    "type": "orphan_closing",
                    "tag": tag,
                    "line": line,
                    "col": col,
                    "detail": f"닫는 태그 </{tag}>에 대응되는 여는 태그가 없음",
                    "index": start_idx
                })
                continue

            open_tag, open_idx = stack.pop()
            if open_tag != tag:
                # 중첩/태그 불일치
                line, col = index_to_linecol(start_idx)
                open_line, open_col = index_to_linecol(open_idx)
                errors.append({
                    "type": "mismatch_or_nesting",
                    "tag": tag,
                    "line": line,
                    "col": col,
                    "detail": f"중첩/불일치: <{open_tag}> (L{open_line}) 안에서 </{tag}>로 닫힘",
                    "index": start_idx,
                    "open_tag": open_tag,
                    "open_line": open_line,
                    "open_col": open_col
                })

    # 닫히지 않은 태그
    for open_tag, open_idx in stack:
        open_line, open_col = index_to_linecol(open_idx)
        errors.append({
            "type": "unclosed_opening",
            "tag": open_tag,
            "line": open_line,
            "col": open_col,
            "detail": f"여는 태그 <{open_tag}>가 닫히지 않음",
            "index": open_idx
        })

    return errors