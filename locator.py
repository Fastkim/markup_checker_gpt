# locator.py
from __future__ import annotations
import re
from typing import Dict, List, Any


_ID_ATTR_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def find_id_occurrences_with_lines(raw_html: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    원본 HTML 기준으로 id="..."가 등장하는 라인 위치를 수집한다.
    반환:
      {
        "some_id": [
          {"line": 123, "snippet": "<div id='some_id'>", "devtools_query": 'id="some_id"'}
        ],
        ...
      }
    """
    lines = raw_html.splitlines()
    id_map: Dict[str, List[Dict[str, Any]]] = {}

    for idx, line in enumerate(lines, start=1):
        # 한 줄에 id가 여러개 있을 수 있어 findall 사용
        ids = _ID_ATTR_RE.findall(line)
        if not ids:
            continue
        for id_val in ids:
            id_map.setdefault(id_val, []).append({
                "line": idx,
                "snippet": line.strip()[:300],  # UI용 스니펫 (너무 길면 자름)
                "devtools_query": f'id="{id_val}"'
            })

    return id_map


def find_duplicate_ids(raw_html: str) -> List[Dict[str, Any]]:
    """
    중복 id만 추려서 이슈 형태로 반환.
    """
    id_map = find_id_occurrences_with_lines(raw_html)
    duplicates = []
    for id_val, occ in id_map.items():
        if len(occ) >= 2:
            duplicates.append({
                "type": "duplicate_id",
                "id": id_val,
                "count": len(occ),
                "evidence": occ[:10],  # 너무 많을 수 있으니 상위 10개만
            })
    # 발견 건수 많은 순으로 정렬
    duplicates.sort(key=lambda x: x["count"], reverse=True)
    return duplicates


def build_evidence_context(raw_html: str, line_no: int, context_lines: int = 2) -> str:
    """
    line_no 주변 컨텍스트(±context_lines)를 문자열로 만들어 준다.
    GPT에 근거로 넣을 때 유용.
    """
    lines = raw_html.splitlines()
    start = max(1, line_no - context_lines)
    end = min(len(lines), line_no + context_lines)

    block = []
    for ln in range(start, end + 1):
        block.append(f"{ln}: {lines[ln-1].rstrip()}")
    return "\n".join(block)
