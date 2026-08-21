#!/usr/bin/env python3
"""渲染 morning.html：包豪斯风 + 笑脸图标 + 四栏。
AI/菌群/德新 来自 build.py 抓取的 RSS JSON；
德语A2/耶拿 来自浏览器抓取的注入 JSON(data/de_a2.json, data/jena.json)，
若为空则显示'今日待刷新'提示，绝不编造。
"""
import json, pathlib, datetime, html

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"

def load(key):
    p = DATA / f"{key}.json"
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: return []
    return []

def esc(s): return html.escape(str(s))

AI = load("ai"); GUT = load("gut"); DENEWS = load("de_news")
DEA2 = load("de_a2"); JENA = load("jena")

def ai_card(x):
    return f'''<article class="card">
  <a class="title" href="{esc(x['url'])}" target="_blank" rel="noopener">{esc(x['title'])}</a>
  <div class="meta"><span class="tag tag-web">{esc(x.get('source',''))}</span></div>
  {('<p class="desc">'+esc(x['desc'])+'</p>') if x.get('desc') else ''}
</article>'''

def gut_card(x):
    return f'''<article class="card">
  <a class="title" href="{esc(x['url'])}" target="_blank" rel="noopener">{esc(x['title'])}</a>
  <div class="meta"><span class="tag tag-topic">{esc(x.get('source','Nature'))}</span></div>
  {('<p class="desc">'+esc(x['desc'])+'</p>') if x.get('desc') else ''}
</article>'''

def news_card(x):
    return f'''<article class="card">
  <a class="title" href="{esc(x['url'])}" target="_blank" rel="noopener">{esc(x['title'])}</a>
  <div class="meta"><span class="tag tag-web">{esc(x.get('source',''))}</span></div>
  {('<p class="desc">'+esc(x['desc'])+'</p>') if x.get('desc') else ''}
</article>'''

def placeholder(msg):
    return f'<article class="card placeholder"><p>{esc(msg)}</p></article>'

def dea2_block():
    if not DEA2:
        return placeholder("德语 A2 今日待刷新 —— 用浏览器抓取 nachrichtenleicht / tagesschau 简易德语后注入。在 Hermes 中说一声\"刷新德语\"即可。")
    parts = []
    for s in DEA2:
        rows = "".join(
            f"<tr><td>{esc(w['w'])}</td><td>{esc(w.get('note',''))}</td><td>{esc(w.get('zh',''))}</td></tr>"
            for w in s.get("words", []))
        gram = "".join(f"<li>{esc(g)}</li>" for g in s.get("grammar", []))
        parts.append(f'''<article class="card de">
  <p class="ger">{esc(s.get('ger',''))}</p>
  <p class="zh">{esc(s.get('zh_full',''))}</p>
  <div class="blk-t">逐词解析 · WORTSCHATZ</div>
  <table class="vocab"><tr><th>词条</th><th>解析（词性/格/时态）</th><th>中文</th></tr>{rows}</table>
  <div class="blk-t">语法详解 · GRAMMATIK</div>
  <ul class="gram">{gram}</ul>
</article>''')
    return "\n".join(parts)

def jena_block():
    if not JENA:
        return placeholder("耶拿本地今日待刷新 —— 浏览器抓取 jena.de / newsroom.jena.de 后注入。说一声\"刷新耶拿\"即可。")
    return "\n".join(
        f'''<article class="card">
  <a class="title" href="{esc(x['url'])}" target="_blank" rel="noopener">{esc(x['title'])}</a>
  <div class="meta"><span class="tag tag-local">{esc(x.get('source','Stadt Jena'))}</span>
  {('<span class="date">'+esc(x['date'])+'</span>') if x.get('date') else ''}</div>
  {('<p class="desc">'+esc(x['desc'])+'</p>') if x.get('desc') else ''}
</article>''' for x in JENA)

today = datetime.date.today().isoformat()
UPD = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

ICON = (ROOT / "icon_v5c.svg").read_text(encoding="utf-8")

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>晨读台 · Morgenbrett</title>
<style>
:root{{--red:#E2231A;--blue:#21409A;--yellow:#FFC400;--ink:#15120c;--paper:#F4F1EA;--line:#dcd6c8;}}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:-apple-system,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;}}
.banner{{display:flex;align-items:center;gap:16px;padding:22px 28px;border-bottom:3px solid var(--ink);background:#fff;}}
.banner .logo{{width:56px;height:56px;flex:0 0 auto;}}
.banner h1{{font-size:26px;margin:0;letter-spacing:.5px;}}
.banner .sub{{font-size:12px;color:#7a7468;margin-top:2px;}}
nav{{display:flex;gap:8px;padding:10px 28px;background:var(--ink);flex-wrap:wrap;}}
nav a{{color:var(--paper);text-decoration:none;font-size:13px;padding:4px 10px;border-radius:4px;opacity:.85;}}
nav a:hover{{opacity:1;background:rgba(255,255,255,.12);}}
.wrap{{max-width:1100px;margin:0 auto;padding:22px 20px 60px;}}
.col h2{{font-size:19px;border-left:8px solid var(--blue);padding-left:10px;margin:30px 0 12px;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr;}}}}
.card{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;}}
.card .title{{display:block;color:var(--ink);text-decoration:none;font-weight:600;font-size:15px;}}
.card .title:hover{{color:var(--blue);text-decoration:underline;}}
.card .desc{{font-size:13px;color:#555;margin:8px 0 0;}}
.meta{{margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;}}
.tag{{font-size:11px;padding:2px 8px;border-radius:20px;color:#fff;}}
.tag-web{{background:var(--red);}}
.tag-topic{{background:var(--blue);}}
.tag-local{{background:var(--yellow);color:var(--ink);}}
.date{{font-size:11px;color:#999;}}
.card.placeholder{{color:#a39c8c;font-style:italic;background:#faf8f2;}}
.card.de{{grid-column:1/-1;}}
.ger{{font-size:17px;font-weight:600;margin:0 0 6px;}}
.zh{{font-size:14px;color:#444;margin:0 0 10px;}}
.blk-t{{font-size:12px;font-weight:700;color:var(--red);margin:10px 0 4px;letter-spacing:.5px;}}
table.vocab{{width:100%;border-collapse:collapse;font-size:13px;margin-top:4px;}}
table.vocab th,table.vocab td{{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top;}}
table.vocab th{{background:#f3efe6;}}
ul.gram{{margin:4px 0 0;padding-left:18px;font-size:13px;color:#444;}}
.foot{{text-align:center;font-size:12px;color:#999;padding:24px;}}
</style>
</head>
<body>
<header class="banner">
  <div class="logo">{ICON}</div>
  <div>
    <h1>晨读台 · MORGENBRETT</h1>
    <div class="sub">每日德语 A2 · AI 快讯 · 肠道菌群 · 耶拿本地 — 更新于 {UPD}</div>
  </div>
</header>
<nav>
  <a href="#de">德语 A2</a><a href="#ai">AI 快讯</a><a href="#gut">肠道菌群</a><a href="#jena">耶拿本地</a>
</nav>
<div class="wrap">
  <section class="col" id="de"><h2>德语 A2 · 每日长句（真实时事）</h2><div class="grid">{dea2_block()}</div></section>
  <section class="col" id="ai"><h2>AI 快讯（多源 RSS）</h2><div class="grid">{"".join(ai_card(x) for x in AI) or placeholder("今日 AI 抓取为空")}</div></section>
  <section class="col" id="gut"><h2>肠道菌群（Nature 等）</h2><div class="grid">{"".join(gut_card(x) for x in GUT) or placeholder("今日菌群抓取为空")}</div></section>
  <section class="col" id="jena"><h2>耶拿本地</h2><div class="grid">{"".join(jena_block() if False else jena_block())}</div></section>
</div>
<footer class="foot">晨读台 · 免费 RSS 驱动 · 每天 07:30 耶拿时间自动更新（GitHub Actions）</footer>
</body>
</html>'''

out = ROOT / "morning.html"
out.write_text(HTML, encoding="utf-8")
print(f"生成 {out}  ({len(HTML)//1024} KB)  AI={len(AI)} 菌群={len(GUT)} 德新={len(DENEWS)} 德A2={len(DEA2)} 耶拿={len(JENA)}")
