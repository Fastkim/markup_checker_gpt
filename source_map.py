# source_map.py
def build_line_starts(text: str):
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts

def index_to_line_col(line_starts, idx: int):
    # 이진 탐색 (빠름)
    lo, hi = 0, len(line_starts) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if line_starts[mid] <= idx:
            lo = mid + 1
        else:
            hi = mid - 1
    line = hi  # 0-based
    col = idx - line_starts[line]
    return (line + 1, col + 1)  # 1-based