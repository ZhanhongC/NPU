#!/usr/bin/env python3
"""扫描 front-matter 重新生成 INDEX.md。用法: python3 00-meta/scripts/index.py"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_DIRS = {"00-meta", ".git"}
QUOTES = chr(34) + chr(39)


def parse_front_matter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        return {}, text
    end = text.find(chr(10) + "---", 3)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip(QUOTES)
    return meta, text[end + 4:]


def first_heading(body):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def collect():
    cases, docs = [], []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(names):
            if not name.endswith(".md") or name in ("INDEX.md", "README.md"):
                continue
            path = os.path.join(base, name)
            rel = os.path.relpath(path, ROOT)
            meta, body = parse_front_matter(path)
            row = {
                "rel": rel,
                "title": meta.get("id") or first_heading(body) or name[:-3],
                "scope": meta.get("scope", ""),
                "platform": meta.get("platform", ""),
                "module": meta.get("module", ""),
                "date": meta.get("date", meta.get("updated", "")),
                "status": meta.get("status", ""),
                "symptom": meta.get("symptom", ""),
            }
            (cases if rel.startswith("50-cases") else docs).append(row)
    return cases, docs


def table(rows, header, keys):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        cells = []
        for i, k in enumerate(keys):
            v = r[k]
            cells.append("[%s](%s)" % (v, r["rel"]) if i == 0 and k == "rel" else v)
        out.append("| " + " | ".join(cells) + " |")
    return out


def main():
    cases, docs = collect()
    cases.sort(key=lambda r: r["date"], reverse=True)
    docs.sort(key=lambda r: r["rel"])
    lines = [
        "# 索引（脚本生成，勿手改）",
        "",
        "重新生成：`python3 00-meta/scripts/index.py`",
        "",
        "## 案例（%d 条，按日期倒序）" % len(cases),
        "",
    ]
    lines += table(cases,
                   ["案例", "日期", "module", "scope", "platform", "状态", "现象"],
                   ["rel", "date", "module", "scope", "platform", "status", "symptom"])
    lines += ["", "## 知识条目（%d 条）" % len(docs), ""]
    lines += table(docs, ["条目", "scope", "platform", "日期"],
                   ["rel", "scope", "platform", "date"])
    lines += [""]
    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(chr(10).join(lines))
    print("INDEX.md: %d cases, %d docs" % (len(cases), len(docs)))


if __name__ == "__main__":
    main()
