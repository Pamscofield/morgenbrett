# 晨读台 · MORGENBRETT

每日早晨阅读聚合（包豪斯风 + 笑脸图标）：
- 德语 A2 长句（真实时事 + 逐词 + 详细语法）
- AI 快讯（TechCrunch / The Verge 多源 RSS）
- 肠道菌群（Nature 等期刊 RSS）
- 耶拿本地（浏览器抓取注入）

## 自动更新
GitHub Actions 每天 **耶拿时间 07:30（UTC 05:30）** 自动抓取免费 RSS 并重建页面。
无需本地开机、无需 Hermes 在线。

## 本地运行
```bash
python morning-app/build.py      # 抓取 RSS -> data/*.json
python morning-app/build_html.py # 生成 morning.html (含笑脸图标)
```
德语 A2 与耶拿本地由浏览器抓取后写入 `morning-app/data/de_a2.json` / `jena.json`（无则显示"今日待刷新"，绝不编造）。

## 数据来源（多源，不局限单站）
- AI: TechCrunch AI, The Verge
- 菌群: Nature Microbiome RSS
- 德新: SPIEGEL International
- 德语 A2: nachrichtenleicht / tagesschau (浏览器注入)
- 耶拿: jena.de / newsroom.jena.de (浏览器注入)
