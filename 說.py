#!/usr/bin/env python3
"""記一句想跟媽媽說的話。

用法：
    python 說.py 要說的話                  新增一則，狀態「想說」
    python 說.py --已說 要說的話           新增一則，狀態「已說」
    python 說.py --已說 --在 靈前 要說的話  同上，並記下在哪裡說的
    python 說.py                           列出全部，並重建 索引.md
"""
import sys
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIR = ROOT / "說"
INDEX = ROOT / "索引.md"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    head, _, body = text.partition("\n\n")
    fields = {}
    for line in head.splitlines():
        m = re.match(r"^(日期|狀態|在)[：:]\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    date = fields.get("日期") or re.sub(r"^(\d{4})(\d{2})(\d{2}).*", r"\1-\2-\3", path.stem)
    return {
        "檔案": path.name,
        "日期": date,
        "狀態": fields.get("狀態", ""),
        "在": fields.get("在", ""),
        "話": body.strip(),
    }


def entries():
    DIR.mkdir(exist_ok=True)
    return sorted((parse(p) for p in DIR.glob("*.md")), key=lambda e: e["檔案"])


def build_index(items):
    lines = ["# 索引", "", "由 說.py 自動產生，不用手改。", ""]
    for e in items:
        first = e["話"].splitlines()[0] if e["話"] else "（空白）"
        where = f"（{e['在']}）" if e["在"] else ""
        lines.append(f"- {e['日期']}　{e['狀態']}{where}　[{first}](說/{e['檔案']})")
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def list_all():
    items = entries()
    if not items:
        print("還沒有任何紀錄。")
        return
    for e in items:
        where = f"（{e['在']}）" if e["在"] else ""
        print(f"{e['日期']}  {e['狀態']}{where}  {e['檔案']}")
        for line in e["話"].splitlines():
            print(f"    {line}")
        print()
    build_index(items)
    print(f"共 {len(items)} 則，索引已更新：{INDEX.name}")


def add(args):
    status = "想說"
    where = ""
    words = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--已說":
            status = "已說"
        elif a == "--想說":
            status = "想說"
        elif a == "--在" and i + 1 < len(args):
            where = args[i + 1]
            i += 1
        else:
            words.append(a)
        i += 1
    text = " ".join(words).strip()
    if not text:
        print(__doc__)
        return
    now = datetime.now()
    DIR.mkdir(exist_ok=True)
    path = DIR / now.strftime("%Y%m%d_%H%M.md")
    n = 2
    while path.exists():
        path = DIR / (now.strftime("%Y%m%d_%H%M") + f"_{n}.md")
        n += 1
    path.write_text(
        f"日期：{now:%Y-%m-%d}\n狀態：{status}\n在：{where}\n\n{text}\n",
        encoding="utf-8",
    )
    print(f"已記下：{path.relative_to(ROOT)}")
    build_index(entries())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_all()
    elif sys.argv[1] in ("-h", "--help"):
        print(__doc__)
    else:
        add(sys.argv[1:])
