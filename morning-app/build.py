#!/usr/bin/env python3
"""晨读台 build.py — 免费 RSS 驱动，零付费额度依赖。
产出 morning.html: AI快讯(多源) / 肠道菌群(Nature) / 德国新闻(SPIEGEL) 全自动；
德语A2 + 耶拿本地 由浏览器抓取后注入 data/*.json (见 refresh 说明)。
GitHub Actions 每天 07:30 耶拿时间(05:30 UTC) 调用本脚本。
"""
import urllib.request, ssl, re, json, html, datetime, pathlib, os

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode("utf-8", "replace")

def items_from_rss(xml):
    # 兼容 RSS <item> 与 Atom <entry>
    out = []
    blocks = re.findall(r"<item[\s\S]*?</item>|<entry[\s\S]*?</entry>", xml, re.I)
    for b in blocks:
        try:
            tm = re.search(r"<title[^>]*>([\s\S]*?)</title>", b, re.I)
            if not tm: continue
            lm = re.search(r"<link[^>]*href=\"([^\"]+)\"[^>]*/>|<link[^>]*>\s*([^<]+?)\s*</link>", b, re.I | re.S)
            dm = re.search(r"<description[^>]*>([\s\S]*?)</description>|<summary[^>]*>([\s\S]*?)</summary>", b, re.I | re.S)
            title = re.sub(r"<[^>]+>", "", tm.group(1)).strip()
            link = ((lm.group(1) if lm else None) or (lm.group(2) if lm else None) or "").strip()
            desc = ""
            if dm:
                desc = (dm.group(1) or dm.group(2) or "")
                desc = re.sub(r"<[^>]+>", " ", desc)
                desc = html.unescape(re.sub(r"\s+", " ", desc)).strip()[:200]
            if title and link:
                out.append({"title": html.unescape(title), "url": link, "desc": desc})
        except Exception as e:
            # 单条坏数据不影响整体
            continue
    return out

FEEDS = {
    "ai": [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("The Verge",     "https://www.theverge.com/rss/index.xml"),
    ],
    "gut": [
        ("Nature Microbiome", "https://www.nature.com/subjects/microbiome.rss"),
    ],
    "de_news": [
        ("SPIEGEL International", "https://www.spiegel.de/international/index.rss"),
    ],
}

def collect(key, n=6):
    out = []
    for src, url in FEEDS[key]:
        try:
            xml = fetch(url)
            for it in items_from_rss(xml):
                it["source"] = src
                out.append(it)
                if len(out) >= n:
                    return out
        except Exception as e:
            print(f"  [warn] {src}: {e}")
    return out[:n]

def dump(key, items):
    (DATA / f"{key}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    today = datetime.date.today().isoformat()
    print(f"[{today}] 抓取免费 RSS ...")
    dump("ai", collect("ai"))
    dump("gut", collect("gut"))
    dump("de_news", collect("de_news"))
    # 德语A2 与 耶拿 由浏览器抓取注入; 若不存在则用空占位并提示
    for k in ("de_a2", "jena"):
        p = DATA / f"{k}.json"
        if not p.exists():
            p.write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")
            print(f"  [note] {k}.json 为空 —— 需浏览器抓取注入(见 refresh 说明)")
    print("完成。运行 build_html.py 生成 morning.html")
