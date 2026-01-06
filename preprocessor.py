"""preprocessor.py

원본 HTML을 받아서:
1) GPT 입력(gpt_input) 생성 (스크립트/스타일 제거 + 길이 제한)
2) detectors(3종) 실행 결과를 issues로 반환

반환 스키마:
{
  "raw_html": str,
  "gpt_input": str,
  "issues": list[dict]
}
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from source_map import build_line_starts, index_to_line_col

from detectors.ids import check_duplicate_ids
from detectors.attributes import check_duplicate_attributes
from detectors.tag_structure import check_tag_structure


def _make_index_to_linecol(raw_html: str):
    line_starts = build_line_starts(raw_html)

    def _fn(idx: int):
        return index_to_line_col(line_starts, idx)

    return _fn


def _line_snippet(raw_html: str, line_no: int, max_len: int = 260) -> str:
    lines = raw_html.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()[:max_len]
    return ""


def _summarize_for_gpt(issues: list[dict], max_items: int = 12) -> str:
    """GPT에 넣을 '후보 이슈 요약' 문자열(짧게)."""
    if not issues:
        return "- (없음)"

    lines = []
    for i, it in enumerate(issues[:max_items], start=1):
        t = it.get("type", "")
        if t == "duplicate_id":
            lines.append(
                f"- ({i}) duplicate_id: id='{it.get('id')}' count={it.get('count')} (예: L{it.get('positions', [{}])[0].get('line', '?')})"
            )
        elif t == "duplicate_attributes":
            lines.append(f"- ({i}) duplicate_attributes: <{it.get('tag')}> L{it.get('line')}")
        elif t in ("orphan_closing", "mismatch_or_nesting", "unclosed_opening"):
            lines.append(f"- ({i}) tag_structure({t}): <{it.get('tag')}> L{it.get('line')}")
        else:
            lines.append(f"- ({i}) {t}: L{it.get('line', '?')}")

    if len(issues) > max_items:
        lines.append(f"- ... (+{len(issues) - max_items} more)")
    return "\n".join(lines)


def preprocess_html(html: str, max_length: int = 6000) -> dict:
    raw_html = html or ""
    index_to_linecol = _make_index_to_linecol(raw_html)

    # 1) detectors 실행
    issues: list[dict] = []
    issues.extend(check_duplicate_ids(raw_html, index_to_linecol))
    issues.extend(check_duplicate_attributes(raw_html, index_to_linecol))
    issues.extend(check_tag_structure(raw_html, index_to_linecol))

    # 2) UI용 evidence 보강 (snippet/devtools_query)
    enriched: list[dict] = []
    for it in issues:
        t = it.get("type")

        if t == "duplicate_id":
            id_val = it.get("id", "")
            ev = []
            for pos in it.get("positions", [])[:10]:
                ln = pos.get("line")
                ev.append(
                    {
                        "line": ln,
                        "col": pos.get("col"),
                        "snippet": _line_snippet(raw_html, int(ln) if ln else 0),
                        "devtools_query": f'id="{id_val}"',
                    }
                )
            it["evidence"] = ev

        else:
            ln = it.get("line")
            if isinstance(ln, int):
                it["snippet"] = _line_snippet(raw_html, ln)

            if "devtools_query" not in it:
                if t == "duplicate_attributes":
                    it["devtools_query"] = f"<{it.get('tag', '')}".strip()
                elif t in ("orphan_closing", "mismatch_or_nesting", "unclosed_opening"):
                    tag = it.get("tag", "")
                    it["devtools_query"] = f"<{tag}" if tag else "<"

        enriched.append(it)

    # 3) GPT 입력 생성(스크립트/스타일 제거)
    soup = BeautifulSoup(raw_html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()

    body = soup.body
    cleaned = str(body) if body else str(soup)
    cleaned = cleaned[:max_length]

    gpt_input = (
        "[페이지 HTML(전처리본)]\n"
        + cleaned
        + "\n\n[검출된 후보 이슈 요약]\n"
        + _summarize_for_gpt(enriched)
    )

    return {
        "raw_html": raw_html,
        "gpt_input": gpt_input,
        "issues": enriched,
    }