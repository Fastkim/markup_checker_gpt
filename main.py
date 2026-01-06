# main.py (완성본)
import json
import tkinter as tk
from tkinter import messagebox, ttk
from config import save_api_key, load_api_key

from fetcher import fetch_html
from preprocessor import preprocess_html
from gpt_judge import judge_markup


def _safe_json_parse(text: str):
    """GPT가 JSON만 출력하도록 했더라도 예외적으로 섞이는 케이스를 대비한 안전 파서."""
    if not text:
        return None
    s = text.strip()

    # 1) 정석: JSON만 오는 경우
    try:
        return json.loads(s)
    except Exception:
        pass

    # 2) 혹시 앞뒤에 잡텍스트가 섞인 경우: 첫 { ~ 마지막 }만 잘라서 시도
    try:
        l = s.find("{")
        r = s.rfind("}")
        if l != -1 and r != -1 and l < r:
            return json.loads(s[l : r + 1])
    except Exception:
        return None

    return None


def _render_gpt_result(out: tk.Text, gpt_raw: str):
    out.insert(tk.END, "=== GPT 판단 결과 ===\n")

    data = _safe_json_parse(gpt_raw)
    if not data:
        # JSON 파싱 실패 시 원문 출력
        out.insert(tk.END, gpt_raw.strip() + "\n\n")
        return

    decision = data.get("decision", "")
    summary = data.get("summary", "")
    violations = data.get("violations", []) or []

    out.insert(tk.END, f"결론: {decision}\n")
    if summary:
        out.insert(tk.END, f"요약: {summary}\n")

    if violations:
        out.insert(tk.END, "\n[위반 상세]\n")
        for v in violations[:30]:
            crit = v.get("criterion", "")
            sev = v.get("severity", "")
            line = v.get("line", "")
            msg = v.get("message", "")
            ev = v.get("evidence", "")

            out.insert(tk.END, f"- (기준 {crit}) ({sev}) line {line}: {msg}\n")
            if ev:
                out.insert(tk.END, f"  evidence: {ev}\n")
    else:
        out.insert(tk.END, "\n(violations 없음)\n")

    out.insert(tk.END, "\n")


def _render_issues(out: tk.Text, issues: list[dict]):
    out.insert(tk.END, "=== 자동 검출 근거(개발자도구 확인용) ===\n")

    if not issues:
        out.insert(tk.END, "- 룰 기반으로 검출된 이슈가 없습니다.\n")
        out.insert(tk.END, "\n")
        return

    for issue in issues[:50]:
        t = issue.get("type", "")

        if t == "duplicate_id":
            out.insert(
                tk.END,
                f"\n[Duplicate ID] id='{issue.get('id')}' / count={issue.get('count')}\n"
            )
            for ev in issue.get("evidence", [])[:10]:
                out.insert(
                    tk.END,
                    f" - line {ev.get('line')}:{ev.get('col')} | {ev.get('snippet','')}\n"
                    f"   devtools_query: {ev.get('devtools_query','')}\n"
                )

        elif t == "duplicate_attributes":
            out.insert(
                tk.END,
                f"\n[Duplicate Attributes] <{issue.get('tag','?')}> "
                f"line {issue.get('line')}:{issue.get('col')}\n"
                f" - {issue.get('detail','')}\n"
                f" - snippet: {issue.get('snippet','')}\n"
                f"   devtools_query: {issue.get('devtools_query','')}\n"
            )

        elif t in ("orphan_closing", "mismatch_or_nesting", "unclosed_opening"):
            out.insert(
                tk.END,
                f"\n[Tag Structure] {t} <{issue.get('tag','?')}> "
                f"line {issue.get('line')}:{issue.get('col')}\n"
                f" - {issue.get('detail','')}\n"
                f" - snippet: {issue.get('snippet','')}\n"
                f"   devtools_query: {issue.get('devtools_query','')}\n"
            )

        else:
            # 예상 못한 타입도 안전하게 표시
            out.insert(
                tk.END,
                f"\n[{t or 'unknown'}] line {issue.get('line','?')}\n"
                f" - {issue.get('detail','')}\n"
            )

    out.insert(tk.END, "\n[확인 팁]\n")
    out.insert(tk.END, "- 크롬: view-source:URL 로 페이지 소스 열고 line 확인\n")
    out.insert(tk.END, "- Elements 탭에서 Ctrl+F로 devtools_query 검색\n\n")


def on_check():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("경고", "검사할 URL을 입력하세요.")
        return

    # 버튼/상태
    check_btn.config(state=tk.DISABLED)
    status_var.set("가져오는 중...")
    root.update_idletasks()

    try:
        html = fetch_html(url)

        status_var.set("전처리/검출 중...")
        root.update_idletasks()
        ctx = preprocess_html(html)

        status_var.set("GPT 판단 중...")
        root.update_idletasks()
        gpt_raw = judge_markup(ctx["gpt_input"])

        # 출력
        result_text.delete("1.0", tk.END)
        _render_gpt_result(result_text, gpt_raw)
        _render_issues(result_text, ctx.get("issues", []))

        status_var.set("완료")

    except Exception as e:
        status_var.set("오류")
        messagebox.showerror("오류", str(e))

    finally:
        check_btn.config(state=tk.NORMAL)
        root.update_idletasks()


def on_clear():
    url_entry.delete(0, tk.END)
    result_text.delete("1.0", tk.END)
    status_var.set("대기")

# api 키 등록
def on_set_api_key():
    win = tk.Toplevel(root)
    win.title("OpenAI API 키 설정")
    win.geometry("520x160")
    win.grab_set()

    ttk.Label(win, text="OpenAI API Key (sk-...):").pack(anchor="w", padx=12, pady=(12, 4))
    entry = ttk.Entry(win, width=70, show="*")
    entry.pack(padx=12, fill=tk.X)

    current = load_api_key()
    if current:
        entry.insert(0, current)

    def save():
        key = entry.get().strip()
        if not key.startswith("sk-"):
            messagebox.showwarning("확인", "키 형식이 올바르지 않습니다. (sk- 로 시작)")
            return
        save_api_key(key)
        messagebox.showinfo("완료", "API 키가 저장되었습니다.")
        win.destroy()

    btns = ttk.Frame(win)
    btns.pack(fill=tk.X, padx=12, pady=12)
    ttk.Button(btns, text="저장", command=save).pack(side=tk.RIGHT)
    ttk.Button(btns, text="닫기", command=win.destroy).pack(side=tk.RIGHT, padx=(0, 8))


# -----------------------------
# UI 생성
# -----------------------------
root = tk.Tk()
root.title("WCAG 2.2 4.1.1 마크업 오류방지 점검기")
root.geometry("980x720")

top = ttk.Frame(root, padding=10)
top.pack(fill=tk.X)

ttk.Label(top, text="대상 URL:").pack(side=tk.LEFT)

url_entry = ttk.Entry(top, width=80)
url_entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)

check_btn = ttk.Button(top, text="검사", command=on_check)
check_btn.pack(side=tk.LEFT, padx=(0, 6))

clear_btn = ttk.Button(top, text="초기화", command=on_clear)
clear_btn.pack(side=tk.LEFT)

# api 키 등록
ttk.Button(top, text="API 키 설정", command=on_set_api_key).pack(side=tk.LEFT, padx=(0, 6))

status_var = tk.StringVar(value="대기")
status_bar = ttk.Label(root, textvariable=status_var, padding=(10, 6))
status_bar.pack(fill=tk.X)

body = ttk.Frame(root, padding=(10, 0, 10, 10))
body.pack(fill=tk.BOTH, expand=True)

result_text = tk.Text(body, wrap=tk.WORD)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll = ttk.Scrollbar(body, orient=tk.VERTICAL, command=result_text.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
result_text.configure(yscrollcommand=scroll.set)

# 단축키
root.bind("<Return>", lambda e: on_check())
root.bind("<Escape>", lambda e: on_clear())

root.mainloop()