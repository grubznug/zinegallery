#!/usr/bin/env python3
import os, re, json

ZINES_DIR = "zines"
OUT = "zines.json"

def read_text(path, limit=None):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read() if limit is None else f.read(limit)
    except Exception as e:
        return ""

def pick_title(html, fallback):
    m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I|re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I|re.S)
    if m:
        txt = re.sub("<[^<]+?>", "", m.group(1))
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            return txt
    return fallback

def pick_description(html):
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', html, flags=re.I|re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r'<meta[^>]+name=["\']zine:description["\'][^>]+content=["\'](.*?)["\']', html, flags=re.I|re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r'<!--\s*zine:description\s*:(.*?)-->', html, flags=re.I|re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m_art = re.search(r'<article\b[^>]*>(.*?)</article>', html, flags=re.I|re.S)
    if m_art:
        body = m_art.group(1)
        text = re.sub("<[^<]+?>", " ", body)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            return (text[:197] + "…") if len(text) > 200 else text
    return ""

def main():
    entries = []
    for root, _, files in os.walk(ZINES_DIR):
        for f in files:
            if not f.lower().endswith(".html"):
                continue
            rel_path = os.path.join(root, f).replace("\\", "/")
            html = read_text(rel_path, limit=200000)
            title = pick_title(html, os.path.basename(rel_path))
            descr = pick_description(html)
            entries.append({"url": rel_path, "title": title, "description": descr})

    entries.sort(key=lambda e: e["url"], reverse=True)

    with open(OUT, "w", encoding="utf-8") as out:
        json.dump(entries, out, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT} with {len(entries)} entries")

if __name__ == "__main__":
    main()
