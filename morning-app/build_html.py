#!/usr/bin/env python3
"""渲染 morning.html —— 视觉 1:1 复刻本地 preview.html 的包豪斯风，
数据来自 build.py 抓取的 RSS JSON (data/*.json)。
日期 = 运行时真实日期 (动态, 不再写死) —— 修复'刷新日期变但内容不变'。
德语A2 / 耶拿 无注入 JSON 时显示'待刷新', 绝不编造。
"""
import json, pathlib, datetime, html, os

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"

def load(key):
    p = DATA / f"{key}.json"
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except Exception: return []
    return []

AI = load("ai"); GUT = load("gut"); DENEWS = load("de_news")
DEA2 = load("de_a2"); JENA = load("jena")

def esc(s): return html.escape(str(s))

def art_class(a):
    return {"der":"art-der","die":"art-die","das":"art-das"}.get(a,"")

def src_pill(src, kind):
    c = "local" if kind=="local" else ("easy" if kind=="easy" else "src")
    return f'<span class="pill {c}">{esc(src)}</span>'

def list_cards(arr, is_jena=False):
    if not arr:
        name = "耶拿本地" if is_jena else "该板块"
        return '<div class="card item"><h3>今日待刷新</h3><p>在 Hermes 中说一声「刷新%s」即可注入真实内容。</p></div>' % name
    out = []
    for it in arr:
        kind = "local" if (is_jena or it.get("local")) else ("easy" if it.get("easy") else "src")
        pills = src_pill(it.get("source",""), kind) + '<span class="pill cat">' + esc(it.get("cat","")) + '</span>'
        why = ('<div class="why">💡 ' + esc(it["why"]) + '</div>') if it.get("why") else ""
        if it.get("url"):
            head = '<a class="headline" href="' + esc(it["url"]) + '" target="_blank" rel="noopener">' + esc(it["title"]) + '</a>'
        else:
            head = esc(it.get("title",""))
        card = '<div class="card item ' + ("jena" if is_jena else "") + '"><h3>' + head + '</h3><p>' + esc(it.get("summary","")) + '</p>\n      <div class="meta">' + pills + '</div>' + why + '</div>'
        out.append(card)
    return "\n".join(out)

# 真实日期 (动态)
now = datetime.datetime.now()
de_date = now.strftime("%d.%m.%Y")
stamp = now.strftime("%Y-%m-%d %H:%M")

HTML = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>晨读台 · Morgenbrett</title>
<style>
  :root{{
    --red:#E2231A; --blue:#21409A; --yellow:#FFC400; --ink:#111111;
    --paper:#F4F1EA; --card:#FFFDF7; --muted:#6b6459;
    --shadow:4px 4px 0 var(--ink);
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    background:var(--paper);color:var(--ink);line-height:1.5}}
  header{{background:var(--ink);color:#fff;padding:26px 30px;position:relative;overflow:hidden}}
  header .geo{{position:absolute;top:0;right:0;height:100%;width:230px}}
  header .date{{font-size:12px;letter-spacing:2px;text-transform:uppercase;opacity:.8}}
  header h1{{margin:6px 0 4px;font-size:30px;font-weight:800;letter-spacing:1px}}
  header .sub{{font-size:13px;opacity:.85;max-width:560px}}
  header .logo{{position:absolute;top:18px;right:24px;width:52px;height:52px;z-index:2}}
  .wrap{{max-width:1180px;margin:0 auto;padding:22px 24px 70px}}
  nav{{position:sticky;top:0;z-index:5;background:rgba(244,241,234,.94);backdrop-filter:blur(6px);
    display:flex;gap:10px;padding:12px 0;flex-wrap:wrap;border-bottom:2px solid var(--ink);margin-bottom:26px}}
  nav a{{font-size:13px;font-weight:700;text-decoration:none;color:var(--ink);background:var(--card);
    border:2px solid var(--ink);padding:8px 14px;border-radius:2px;box-shadow:3px 3px 0 var(--ink)}}
  nav a:hover{{background:var(--yellow)}}
  section{{margin-bottom:48px;scroll-margin-top:70px}}
  .sec-head{{display:flex;align-items:center;gap:14px;margin-bottom:16px;
    border-bottom:4px solid var(--ink);padding-bottom:8px}}
  .sec-head svg{{width:46px;height:46px;flex:none;border:2px solid var(--ink)}}
  .sec-head h2{{margin:0;font-size:21px;font-weight:800}}
  .sec-head .em{{font-size:12.5px;color:var(--muted);font-weight:600}}
  .sec-head .stamp{{margin-left:auto;font-size:12px;color:var(--muted);font-weight:700}}
  .grid{{display:grid;gap:18px}}
  .grid.de{{grid-template-columns:1fr}}
  @media(min-width:820px){{.grid.de{{grid-template-columns:1fr 1fr}}}}
  .grid.list{{grid-template-columns:1fr}}
  @media(min-width:900px){{.grid.list{{grid-template-columns:1fr 1fr}}}}
  .card{{background:var(--card);border:2px solid var(--ink);border-radius:4px;padding:16px 18px;box-shadow:var(--shadow)}}
  .card.de{{border-top:8px solid var(--blue)}}
  .card.ai{{border-top:8px solid var(--red)}}
  .card.gut{{border-top:8px solid var(--yellow)}}
  .card.jena{{border-top:8px solid var(--ink)}}
  .de .ger{{font-size:18px;font-weight:700;margin-bottom:4px}}
  .de .zh{{color:#4a443b;font-size:14px;margin-bottom:12px;font-weight:600}}
  .de .blk-t{{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin:12px 0 6px}}
  table.vocab{{width:100%;border-collapse:collapse;font-size:12.5px}}
  table.vocab th{{text-align:left;background:var(--paper);border:1px solid var(--ink);padding:4px 7px;font-size:11px}}
  table.vocab td{{border:1px solid var(--ink);padding:4px 7px;vertical-align:top}}
  .art-der{{color:var(--red)}} .art-die{{color:var(--blue)}} .art-das{{color:#1d7a3a}}
  .pl{{color:var(--muted);font-size:11px}}
  .grammar{{font-size:13px;background:#fff;border-left:6px solid var(--blue);padding:10px 12px;margin-top:4px}}
  .grammar li{{margin-bottom:5px}}
  .grammar .en{{display:block;color:var(--muted);font-style:italic;font-size:12px;margin-top:8px;border-top:1px dashed var(--ink);padding-top:6px}}
  .item h3{{margin:0 0 6px;font-size:15.5px;line-height:1.4;font-weight:700}}
  .item p{{margin:0 0 9px;font-size:13.5px;color:#4a443b}}
  .meta{{display:flex;gap:7px;flex-wrap:wrap;align-items:center}}
  .pill{{font-size:11px;padding:3px 9px;border-radius:2px;font-weight:700;border:1.5px solid var(--ink)}}
  .pill.cat{{background:var(--blue);color:#fff}}
  .pill.src{{background:var(--red);color:#fff}}
  .pill.local{{background:var(--yellow);color:var(--ink)}}
  .pill.easy{{background:#fff;color:var(--ink)}}
  .item a.headline{{color:var(--ink);text-decoration:none}}
  .item a.headline:hover{{text-decoration:underline;color:var(--red)}}
  .why{{font-size:12px;color:var(--muted);margin-top:8px;border-top:1px dashed var(--ink);padding-top:7px;font-weight:600}}
  footer{{text-align:center;color:var(--muted);font-size:12px;padding:24px;border-top:2px solid var(--ink)}}
</style>
</head>
<body>
<header>
  <div class="date" id="date">{de_date}</div>
  <h1>晨读台 · MORGENBRETT</h1>
  <div class="sub">德语 A2 · AI 快讯 · 肠道菌群 · 耶拿本地 — 每天早晨，开电脑即读</div>
</header>

<div class="wrap">
  <nav>
    <a href="#de">▦ 德语 A2</a>
    <a href="#ai">● AI 快讯</a>
    <a href="#gut">◐ 肠道菌群</a>
    <a href="#jena">▲ 耶拿本地</a>
  </nav>

  <section id="de">
    <div class="sec-head">
      <svg viewBox="0 0 48 48"><rect width="48" height="48" fill="#fff" stroke="#111" stroke-width="3"/>
        <circle cx="15" cy="15" r="9" fill="var(--blue)"/>
        <rect x="27" y="25" width="13" height="13" fill="var(--red)"/>
        <polygon points="27,7 41,7 34,19" fill="var(--yellow)"/></svg>
      <h2>德语 A2 · 每日长句</h2>
      <span class="em">真实时事主题（nachrichtenleicht / tagesschau）· 逐词解析 · 详细语法</span>
      <span class="stamp">更新于 {stamp}</span>
    </div>
    <div class="grid list" id="de-grid">{list_cards(DEA2)}</div>
  </section>

  <section id="ai">
    <div class="sec-head">
      <svg viewBox="0 0 48 48"><rect width="48" height="48" fill="#fff" stroke="#111" stroke-width="3"/>
        <line x1="14" y1="14" x2="34" y2="20" stroke="#111" stroke-width="2"/>
        <line x1="14" y1="14" x2="24" y2="36" stroke="#111" stroke-width="2"/>
        <line x1="34" y1="20" x2="24" y2="36" stroke="#111" stroke-width="2"/>
        <circle cx="14" cy="14" r="6" fill="var(--red)"/>
        <circle cx="34" cy="20" r="6" fill="var(--blue)"/>
        <circle cx="24" cy="36" r="6" fill="var(--yellow)"/></svg>
      <h2>AI 快讯（多源 RSS 自动抓取）</h2>
      <span class="em">TechCrunch / The Verge</span>
      <span class="stamp">更新于 {stamp}</span>
    </div>
    <div class="grid list" id="ai-grid">{list_cards(AI)}</div>
  </section>

  <section id="gut">
    <div class="sec-head">
      <svg viewBox="0 0 48 48"><rect width="48" height="48" fill="#fff" stroke="#111" stroke-width="3"/>
        <circle cx="17" cy="18" r="8" fill="var(--yellow)"/>
        <circle cx="31" cy="22" r="7" fill="var(--blue)"/>
        <circle cx="22" cy="33" r="6" fill="var(--red)"/>
        <line x1="17" y1="18" x2="31" y2="22" stroke="#111" stroke-width="1.5"/>
        <line x1="31" y1="22" x2="22" y2="33" stroke="#111" stroke-width="1.5"/></svg>
      <h2>肠道菌群 · 最新研究（Nature RSS）</h2>
      <span class="em">Nature Microbiome 等期刊</span>
      <span class="stamp">更新于 {stamp}</span>
    </div>
    <div class="grid list" id="gut-grid">{list_cards(GUT)}</div>
  </section>

  <section id="jena">
    <div class="sec-head">
      <svg viewBox="0 0 48 48"><rect width="48" height="48" fill="#fff" stroke="#111" stroke-width="3"/>
        <rect x="20" y="8" width="10" height="34" fill="var(--yellow)"/>
        <circle cx="13" cy="14" r="6" fill="var(--blue)"/>
        <rect x="8" y="42" width="32" height="4" fill="var(--red)"/></svg>
      <h2>耶拿本地</h2>
      <span class="em">官方源 jena.de / Stadt Jena</span>
      <span class="stamp">更新于 {stamp}</span>
    </div>
    <div class="grid list" id="jena-grid">{list_cards(JENA, is_jena=True)}</div>
  </section>

  <footer>晨读台 · 免费 RSS 驱动 · 每天 07:30 耶拿时间自动更新（GitHub Actions）· 数据来源见每卡「来源」标签</footer>
</div>
</body>
</html>'''

out = ROOT / "morning.html"
out.write_text(HTML, encoding="utf-8")
print(f"生成 morning.html ({len(HTML)//1024} KB) AI={len(AI)} 菌群={len(GUT)} 德新={len(DENEWS)} 德A2={len(DEA2)} 耶拿={len(JENA)} 日期={de_date}")
