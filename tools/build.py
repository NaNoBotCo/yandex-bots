#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build docs/index.html (English) and docs/th/index.html (Thai) from docs/data.json.

Numbers on the page are computed here from the baked Radar series, so the copy and the
charts read the same file. `python3 tools/data.py` re-pulls; `python3 tools/build.py` rebuilds.
"""
import json, os, html

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = json.load(open(os.path.join(ROOT, "docs", "data.json")))
H = D["hours"]
NET = {n["key"]: n for n in D["nets"]}


def day_mean(key, field, day, h0=0, h1=24):
    v = [x for t, x in zip(H, NET[key][field]) if t[:10] == day and h0 <= int(t[11:13]) < h1]
    return sum(v) / len(v)


def change(key, field="bots", a="2026-10-04", b="2026-10-11"):
    return day_mean(key, field, b) / day_mean(key, field, a) - 1


def ru_share(day, asn):
    top = next(x for x in D["ruTop"] if x["day"] == day)["top"]
    return next((x["pct"] for x in top if x["asn"] == asn), None)


# ---- the numbers -------------------------------------------------------------------
N = {}
N["y"] = change("yandex")
N["yc"] = change("ycloud")
N["ru"] = change("ru")
N["yh"] = change("yandex", "humans")
N["ys4"] = ru_share("2026-10-04", 13238)
N["ys11"] = ru_share("2026-10-11", 13238) or 0
N["ycs4"] = ru_share("2026-10-04", 200350)
N["yown"] = NET["yandex"]["botShare"]["pct"][NET["yandex"]["botShare"]["days"].index("2026-10-04")]
N["step8"] = day_mean("yandex", "bots", "2026-10-08", 8, 24) / day_mean("yandex", "bots", "2026-10-08", 0, 8) - 1
# waterfall, in points of Russia's Oct 4 bot traffic
N["wf_y"] = N["ys4"] * N["y"]
N["wf_yc"] = N["ycs4"] * N["yc"]
N["wf_ru"] = N["ru"] * 100
N["wf_rest"] = N["wf_ru"] - N["wf_y"] - N["wf_yc"]
N["rest"] = N["wf_rest"] / (100 - N["ys4"] - N["ycs4"])
N["explained"] = (N["wf_y"] + N["wf_yc"]) / N["wf_ru"]
TABLE = [(n["key"], n["en"], n["th"], change(n["key"]), change(n["key"], "humans")) for n in D["nets"]]


def pct(x, signed=True, dp=0):
    s = f"{x * 100:+.{dp}f}%" if signed else f"{x * 100:.{dp}f}%"
    return s.replace("-", "−")


def pts(x, dp=1):
    return f"{x:+.{dp}f}".replace("-", "−")


# ---- copy ---------------------------------------------------------------------------
T = {
 "en": dict(
  lang="en", title="The Crawler Went Quiet", other="th/", other_label="ไทย",
  desc=f"Hour by hour, from Cloudflare Radar: drone strikes on Yandex data centers, 8–11 October 2026, and what happened to automated traffic from Yandex and the rest of Russia.",
  kicker="Cloudflare Radar · 8–11 October 2026",
  lede=f"Drones struck Yandex data centers in Sasovo, Kaluga and Vladimir between 8 and 11 October 2026. "
       f"Automated traffic from Yandex's network, as Cloudflare counts it, fell {pct(-N['y'], False)} in a day. "
       f"Automated traffic from the rest of Russia barely moved: {pct(N['rest'], True, 1)}.",
  hint="Drag across the chart. Tap the spider.",
  nav=[("hours", "Hours"), ("networks", "Networks"), ("russia", "Russia"), ("sum", "Sum"), ("bots", "Bots"), ("data", "Data")],
  slab=[
   (pct(N["y"]), "Yandex bots", "Sun 11 Oct vs Sun 4 Oct"),
   (pct(N["yc"]), "Yandex Cloud bots", "same days"),
   (pct(N["ru"]), "All Russian bots", "same days"),
   (pct(N["rest"], True, 1), "Russia without Yandex", "same days"),
   (f"{N['explained'] * 100:.0f}%", "of Russia's drop", "is Yandex"),
   (f"{N['yown']:.1f}%", "of Yandex's traffic", "was bots, 4 Oct"),
  ],
  tip_bots="bots", tip_hum="humans", tip_base="of the 21 Sep–6 Oct average",
  axis_base="baseline = 100", legend_bots="Bots", legend_hum="Humans",
  h_hours="Hour by hour",
  p_hours=[
   "<b>1 Oct 05:00 – 2 Oct 06:00 UTC.</b> A week before the first strike, Yandex's bot traffic sat near 40 for 26 hours. No strike was reported.",
   f"<b>8 Oct, 08:00 UTC.</b> Sasovo, Ryazan region, overnight. Yandex's bot traffic steps down {pct(-N['step8'], False)} within the hour and holds there.",
   "<b>9 Oct.</b> Kaluga. Reported struck; the series shows no step that day.",
   "<b>11 Oct, 00:00–02:00 UTC.</b> Vladimir. Yandex said operations at the facility were suspended. Bot traffic goes under 1% of its three-week peak from 01:00 to 13:00 UTC, flickers back to about a fifth of normal at 15:00, and settles near a tenth.",
   f"Human traffic from the same network fell {pct(-N['yh'], False)} on 11 Oct. The whole network went dark, not the bots alone.",
  ],
  strikes=[("2026-10-08T00:00:00Z", "Sasovo"), ("2026-10-09T00:00:00Z", "Kaluga"), ("2026-10-11T00:00:00Z", "Vladimir")],
  h_net="Ten networks, one scale",
  p_net="Each panel is one network's automated traffic, 100 = its own 21 September–6 October average. Same scale everywhere. Tap a panel.",
  p_net2="Human traffic from Russia's mobile networks rose on 11 October. Radar's data doesn't say why.",
  h_ru="Yandex's share of Russia's bots",
  p_ru=f"Of all automated requests from Russian networks, Yandex sent {N['ys4']:.1f}% on 4 October and {N['ys11']:.1f}% on 11 October. It had been the second-largest sender every day since 28 September; on 11 October it was 23rd.",
  h_sum="Where Russia's 10% went",
  p_sum=f"Russia's bot traffic on 4 October = 100. Each network's loss = its share that day × how far it fell.",
  wf=[("4 Oct", "total"), ("Yandex", "step"), ("Yandex Cloud", "step"), ("everyone else", "step"), ("11 Oct", "total")],
  eq=f"Yandex: {N['ys4']:.2f} × {pct(N['y'], True, 1)} = {pts(N['wf_y'], 2)}<br>"
     f"Yandex Cloud: {N['ycs4']:.2f} × {pct(N['yc'], True, 1)} = {pts(N['wf_yc'], 2)}<br>"
     f"All of Russia: 100 × {pct(N['ru'], True, 1)} = {pts(N['wf_ru'], 2)}<br>"
     f"Everyone else: {pts(N['wf_ru'], 2)} − ({pts(N['wf_y'], 2)}) − ({pts(N['wf_yc'], 2)}) = {pts(N['wf_rest'], 2)} on a base of {100 - N['ys4'] - N['ycs4']:.2f} → {pct(N['rest'], True, 1)}",
  h_bots="Which bots",
  p_bots=[
   "Radar sorts each request reaching a Cloudflare-served site as likely human or likely automated. It counts requests, not operators or purposes.",
   f"Before the strikes, {N['yown']:.1f}% of Yandex's requests were automated. Yandex runs a search crawler that indexes the web; Radar's per-network counts don't say which Yandex service sent a request.",
   "A request from a server outside Russia counts under that server's country. Bots run from foreign servers, home connections or phones don't show up as Yandex.",
   "So the drop measures Yandex's own machines going offline. Whether any influence operation slowed is a separate question this data can't answer.",
  ],
  tbl_cap="Sunday 11 October against Sunday 4 October, daily mean of hourly values",
  tbl_head=("Network", "Bots", "Humans"),
  h_data="Data",
  p_data=[
   'Every series on this page: <a href="{base}data.json">data.json</a>, pulled from the Cloudflare Radar API '
   f'(HTTP requests by bot class, hourly, 21 Sep–11 Oct 2026; top networks by day; pulled {D["pulled"]}). '
   'Each hourly series is divided by its own 21 September–6 October mean.',
   'Reporting: <a href="https://thedeepdive.ca/bot-traffic-from-yandexs-network-falls-to-near-zero-after-third-drone-strike/">The Deep Dive</a>, '
   '<a href="https://runtimewire.com/article/bluesky-yandex-bot-traffic-cloudflare-radar">RuntimeWire</a>, '
   '<a href="https://www.tomshardware.com/tech-industry/data-centers/russian-disinformation-bot-traffic-nearly-eliminated-overnight-after-ukraine-drone-strikes-cripple-multiple-of-russias-google-data-centers-ukraine-intensifies-bombing-of-yandex-data-centers-in-response-to-moscows-strikes-on-kyiv-data-centers">Tom\'s Hardware</a>. '
   'Ukraine has not formally claimed the strikes; Yandex named a drone attack for Vladimir.',
  ],
  foot='Data: <a href="https://radar.cloudflare.com/">Cloudflare Radar</a>, CC BY-NC 4.0. Text and drawings: CC BY 4.0, NaNoBotCo. Code: MIT.',
 ),
 "th": dict(
  lang="th", title="เมื่อแมงมุมของยานเดกซ์หลับ", other="../", other_label="EN",
  desc="รายชั่วโมงจาก Cloudflare Radar: โดรนโจมตีศูนย์ข้อมูลยานเดกซ์ 8–11 ตุลาคม 2026 และทราฟฟิกอัตโนมัติจากยานเดกซ์และส่วนอื่นของรัสเซีย",
  kicker="Cloudflare Radar · 8–11 ตุลาคม 2026",
  lede=f"ระหว่างวันที่ 8–11 ตุลาคม 2026 โดรนโจมตีศูนย์ข้อมูลของยานเดกซ์ที่ซาโซโว คาลูกา และวลาดิเมียร์ "
       f"ทราฟฟิกอัตโนมัติจากเครือข่ายยานเดกซ์ตามที่ Cloudflare นับ ลดลง {pct(-N['y'], False)} ภายในวันเดียว "
       f"ส่วนทราฟฟิกอัตโนมัติจากรัสเซียส่วนที่เหลือแทบไม่เปลี่ยน: {pct(N['rest'], True, 1)}",
  hint="ลากนิ้วไปบนกราฟ แตะแมงมุม",
  nav=[("hours", "รายชั่วโมง"), ("networks", "เครือข่าย"), ("russia", "รัสเซีย"), ("sum", "ผลรวม"), ("bots", "บอต"), ("data", "ข้อมูล")],
  slab=[
   (pct(N["y"]), "บอตยานเดกซ์", "อา. 11 ต.ค. เทียบ อา. 4 ต.ค."),
   (pct(N["yc"]), "บอตยานเดกซ์คลาวด์", "วันเดียวกัน"),
   (pct(N["ru"]), "บอตทั้งรัสเซีย", "วันเดียวกัน"),
   (pct(N["rest"], True, 1), "รัสเซียไม่รวมยานเดกซ์", "วันเดียวกัน"),
   (f"{N['explained'] * 100:.0f}%", "ของส่วนที่รัสเซียลดลง", "มาจากยานเดกซ์"),
   (f"{N['yown']:.1f}%", "ของทราฟฟิกยานเดกซ์", "เป็นบอต 4 ต.ค."),
  ],
  tip_bots="บอต", tip_hum="คน", tip_base="ของค่าเฉลี่ย 21 ก.ย.–6 ต.ค.",
  axis_base="ฐาน = 100", legend_bots="บอต", legend_hum="คน",
  h_hours="รายชั่วโมง",
  p_hours=[
   "<b>1 ต.ค. 05:00 – 2 ต.ค. 06:00 UTC</b> หนึ่งสัปดาห์ก่อนการโจมตีครั้งแรก ทราฟฟิกบอตของยานเดกซ์อยู่ราว 40 นาน 26 ชั่วโมง ไม่มีรายงานการโจมตี",
   f"<b>8 ต.ค. 08:00 UTC</b> ซาโซโว แคว้นรียาซาน ช่วงกลางคืน ทราฟฟิกบอตของยานเดกซ์ลดลง {pct(-N['step8'], False)} ภายในชั่วโมงเดียวและคงอยู่ระดับนั้น",
   "<b>9 ต.ค.</b> คาลูกา มีรายงานว่าถูกโจมตี แต่กราฟไม่มีขั้นลดในวันนั้น",
   "<b>11 ต.ค. 00:00–02:00 UTC</b> วลาดิเมียร์ ยานเดกซ์แจ้งว่าหยุดการทำงานของศูนย์นั้น ทราฟฟิกบอตต่ำกว่า 1% ของจุดสูงสุดในสามสัปดาห์ ตั้งแต่ 01:00 ถึง 13:00 UTC กลับขึ้นมาราวหนึ่งในห้าตอน 15:00 แล้วอยู่ราวหนึ่งในสิบ",
   f"ทราฟฟิกจากคนในเครือข่ายเดียวกันลดลง {pct(-N['yh'], False)} ในวันที่ 11 ต.ค. ทั้งเครือข่ายดับ ไม่ใช่แค่บอต",
  ],
  strikes=[("2026-10-08T00:00:00Z", "ซาโซโว"), ("2026-10-09T00:00:00Z", "คาลูกา"), ("2026-10-11T00:00:00Z", "วลาดิเมียร์")],
  h_net="สิบเครือข่าย สเกลเดียว",
  p_net="แต่ละช่องคือทราฟฟิกอัตโนมัติของเครือข่ายหนึ่ง 100 = ค่าเฉลี่ยของเครือข่ายนั้นเองระหว่าง 21 ก.ย.–6 ต.ค. ทุกช่องใช้สเกลเดียวกัน แตะที่ช่องได้",
  p_net2="ทราฟฟิกจากคนบนเครือข่ายมือถือของรัสเซียเพิ่มขึ้นในวันที่ 11 ต.ค. ข้อมูล Radar ไม่ได้บอกสาเหตุ",
  h_ru="สัดส่วนของยานเดกซ์ในบอตทั้งรัสเซีย",
  p_ru=f"จากคำขออัตโนมัติทั้งหมดจากเครือข่ายรัสเซีย ยานเดกซ์ส่ง {N['ys4']:.1f}% ในวันที่ 4 ต.ค. และ {N['ys11']:.1f}% ในวันที่ 11 ต.ค. ยานเดกซ์เป็นผู้ส่งอันดับสองทุกวันตั้งแต่ 28 ก.ย. และตกไปอยู่อันดับ 23 ในวันที่ 11 ต.ค.",
  h_sum="10% ของรัสเซียหายไปไหน",
  p_sum="ทราฟฟิกบอตของรัสเซียวันที่ 4 ต.ค. = 100 ส่วนที่แต่ละเครือข่ายเสียไป = สัดส่วนของมันในวันนั้น × ระดับที่ลดลง",
  wf=[("4 ต.ค.", "total"), ("ยานเดกซ์", "step"), ("ยานเดกซ์คลาวด์", "step"), ("ที่เหลือ", "step"), ("11 ต.ค.", "total")],
  eq=None,
  h_bots="บอตแบบไหน",
  p_bots=[
   "Radar แยกคำขอแต่ละรายการที่เข้าเว็บไซต์ที่ใช้ Cloudflare ว่าน่าจะมาจากคนหรือจากระบบอัตโนมัติ นับเป็นคำขอ ไม่ได้บอกว่าใครเป็นผู้ดำเนินการหรือทำไปเพื่ออะไร",
   f"ก่อนการโจมตี {N['yown']:.1f}% ของคำขอจากยานเดกซ์เป็นอัตโนมัติ ยานเดกซ์มีโปรแกรมรวบรวมข้อมูลของเสิร์ชเอนจินที่ไล่อ่านเว็บ แต่ตัวเลขของ Radar รายเครือข่ายไม่ได้บอกว่าคำขอมาจากบริการไหนของยานเดกซ์",
   "คำขอจากเซิร์ฟเวอร์นอกรัสเซียนับเป็นของประเทศที่เซิร์ฟเวอร์ตั้งอยู่ บอตที่รันจากเซิร์ฟเวอร์ต่างประเทศ อินเทอร์เน็ตบ้าน หรือโทรศัพท์ จะไม่ปรากฏเป็นยานเดกซ์",
   "ตัวเลขที่ลดลงจึงวัดเครื่องของยานเดกซ์เองที่ดับไป ส่วนปฏิบัติการชี้นำความคิดใดชะลอลงหรือไม่ ข้อมูลนี้ตอบไม่ได้",
  ],
  tbl_cap="อาทิตย์ 11 ต.ค. เทียบ อาทิตย์ 4 ต.ค. ค่าเฉลี่ยรายวันจากค่ารายชั่วโมง",
  tbl_head=("เครือข่าย", "บอต", "คน"),
  h_data="ข้อมูล",
  p_data=[
   'ทุกชุดข้อมูลบนหน้านี้: <a href="{base}data.json">data.json</a> ดึงจาก Cloudflare Radar API '
   f'(คำขอ HTTP แยกตามประเภทบอต รายชั่วโมง 21 ก.ย.–11 ต.ค. 2026 และเครือข่ายอันดับต้นรายวัน ดึงเมื่อ {D["pulled"]}) '
   'แต่ละชุดหารด้วยค่าเฉลี่ยของตัวเองช่วง 21 ก.ย.–6 ต.ค.',
   'รายงานข่าว: <a href="https://thedeepdive.ca/bot-traffic-from-yandexs-network-falls-to-near-zero-after-third-drone-strike/">The Deep Dive</a>, '
   '<a href="https://runtimewire.com/article/bluesky-yandex-bot-traffic-cloudflare-radar">RuntimeWire</a>, '
   '<a href="https://www.tomshardware.com/tech-industry/data-centers/russian-disinformation-bot-traffic-nearly-eliminated-overnight-after-ukraine-drone-strikes-cripple-multiple-of-russias-google-data-centers-ukraine-intensifies-bombing-of-yandex-data-centers-in-response-to-moscows-strikes-on-kyiv-data-centers">Tom\'s Hardware</a> '
   'ยูเครนยังไม่ได้ประกาศอย่างเป็นทางการว่าเป็นผู้โจมตี ยานเดกซ์ระบุว่าวลาดิเมียร์ถูกโดรนโจมตี',
  ],
  foot='ข้อมูล: <a href="https://radar.cloudflare.com/">Cloudflare Radar</a>, CC BY-NC 4.0 ข้อความและภาพวาด: CC BY 4.0, NaNoBotCo โค้ด: MIT',
 ),
}
T["th"]["eq"] = T["en"]["eq"].replace("Yandex Cloud", "ยานเดกซ์คลาวด์").replace("Yandex", "ยานเดกซ์").replace(
    "All of Russia", "ทั้งรัสเซีย").replace("Everyone else", "ที่เหลือ").replace("on a base of", "บนฐาน")

CSS = """
:root{color-scheme:light dark;
 --bg:#fff7ec;--panel:#fff;--ink:#1c1530;--mute:#675c77;--line:#f0dcc4;--accent:#f04a00;--gold:#ffb000;--grid:#e9d8c4;--shadow:rgba(60,20,0,.14);
 --night:#16112a;--night-ink:#fbf2e8;--night-mute:#bcb0cc;--night-grid:#3a2f55;
 --display:"Avenir Next Condensed","HelveticaNeue-CondensedBold","Arial Narrow Bold","Franklin Gothic Heavy",Impact,system-ui,sans-serif;
 --body:"Avenir Next",Avenir,"Segoe UI",system-ui,-apple-system,Helvetica,Arial,sans-serif;
 --thai:"Noto Sans Thai","Leelawadee UI","Thonburi","Sukhumvit Set",Tahoma,sans-serif;
 --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --bg:#120d20;--panel:#1d1631;--ink:#fbf2e8;--mute:#bcb0cc;--line:#352a4d;--accent:#ff7a3d;--gold:#ffc53d;--grid:#2e2546;--shadow:rgba(0,0,0,.5)}}
:root[data-theme="dark"]{--bg:#120d20;--panel:#1d1631;--ink:#fbf2e8;--mute:#bcb0cc;--line:#352a4d;--accent:#ff7a3d;--gold:#ffc53d;--grid:#2e2546;--shadow:rgba(0,0,0,.5)}
*{box-sizing:border-box}
html{font-size:18px;scroll-behavior:smooth;scroll-padding-top:3.5rem}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);line-height:1.6;-webkit-text-size-adjust:100%;overflow-x:hidden}
:lang(th),.th{font-family:var(--thai);line-height:1.85}
a{color:var(--accent);text-underline-offset:.18em}
a:focus-visible,button:focus-visible{outline:3px solid var(--gold);outline-offset:2px;border-radius:6px}
.wrap{max-width:62rem;margin:0 auto;padding:0 16px}
header.top{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:3px solid var(--accent)}
header.top .wrap{display:flex;align-items:center;gap:.4rem 1rem;flex-wrap:wrap;padding-top:.45rem;padding-bottom:.45rem}
.brand{font-family:var(--display);font-weight:800;font-size:1.05rem;text-transform:uppercase;text-decoration:none;color:var(--ink);white-space:nowrap}
:lang(th) .brand{font-family:var(--thai);text-transform:none}
header.top nav{display:flex;gap:.1rem .75rem;flex-wrap:wrap;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;font-weight:800}
:lang(th) header.top nav{text-transform:none;letter-spacing:0;font-size:.8rem}
header.top nav a{text-decoration:none;color:var(--mute)}
header.top nav a:hover{color:var(--ink);box-shadow:inset 0 -3px 0 var(--accent)}
.langsw{margin-left:auto;font-size:.74rem;font-weight:800;text-decoration:none;padding:.15rem .6rem;border:2px solid var(--line);border-radius:99px;color:var(--mute)}
.hero{background:var(--night);color:var(--night-ink);padding:2.2rem 0 1rem;border-bottom:4px solid var(--accent)}
.kicker{display:block;font-family:var(--display);font-size:.72rem;font-weight:800;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin-bottom:.4rem}
:lang(th) .kicker{font-family:var(--thai);letter-spacing:.05em}
h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(2.4rem,8vw,5rem);line-height:.88;margin:0 0 .8rem;max-width:12ch}
.hero .lede{max-width:40rem;color:#fff1e2;font-size:clamp(1rem,2.2vw,1.15rem);margin:0 0 .6rem}
.hint{font-size:.78rem;color:var(--night-mute);margin:.2rem 0 .4rem}
.chart{position:relative;width:100%;touch-action:pan-y}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
#hero-chart{margin-top:.4rem}
h2{font-family:var(--display);font-size:clamp(1.8rem,5vw,2.8rem);line-height:.95;margin:3rem 0 .8rem;font-weight:800;text-transform:uppercase;padding-bottom:.8rem;border-bottom:3px solid var(--ink)}
:lang(th) h1,:lang(th) h2{font-family:var(--thai);text-transform:none;line-height:1.2}
p{max-width:44rem}
.slab{display:grid;grid-template-columns:repeat(auto-fit,minmax(8rem,1fr));gap:.7rem;margin:1.6rem 0 0}
.slab button{all:unset;cursor:pointer;padding:.9rem .8rem;border-radius:18px;background:var(--panel);box-shadow:0 8px 24px -14px var(--shadow);position:relative;overflow:hidden;display:block;transition:transform .15s}
.slab button:active{transform:scale(.96) rotate(-1deg)}
.slab button:focus-visible{outline:3px solid var(--gold)}
.slab b{display:block;font-family:var(--display);font-size:clamp(1.8rem,4.4vw,2.6rem);line-height:.92;font-weight:800;color:var(--accent)}
.slab span{display:block;font-size:.66rem;text-transform:uppercase;letter-spacing:.1em;color:var(--ink);font-weight:800;margin-top:.35rem}
.slab i{display:block;font-style:normal;font-size:.72rem;color:var(--mute);margin-top:.1rem}
:lang(th) .slab span{letter-spacing:0;font-size:.8rem;text-transform:none}
.steps p{border-left:4px solid var(--accent);padding-left:.8rem;margin:.7rem 0}
.legend{display:flex;gap:1.2rem;font-size:.8rem;font-weight:700;color:var(--mute);margin:.4rem 0}
.legend span{display:inline-flex;align-items:center;gap:.4rem}
.legend svg{width:28px;height:10px}
.grid10{display:grid;grid-template-columns:repeat(auto-fill,minmax(11.5rem,1fr));gap:.7rem}
.panel{all:unset;cursor:pointer;display:block;background:var(--panel);border-radius:16px;padding:.55rem .6rem .3rem;box-shadow:0 8px 24px -16px var(--shadow)}
.panel:focus-visible{outline:3px solid var(--gold)}
.panel .nm{font-weight:800;font-size:.82rem;display:flex;justify-content:space-between;gap:.4rem}
.panel .nm em{font-style:normal;color:var(--accent);font-family:var(--display);font-size:1rem}
.panel svg{display:block;width:100%;height:auto}
.box{background:var(--panel);border-radius:20px;padding:1rem;box-shadow:0 10px 30px -18px var(--shadow)}
.eq{font-family:var(--mono);font-size:.8rem;line-height:1.7;background:var(--panel);border-radius:14px;padding:.8rem 1rem;overflow-x:auto;margin:1rem 0;box-shadow:0 8px 24px -16px var(--shadow)}
table{border-collapse:collapse;width:100%;max-width:34rem;font-size:.86rem;margin:.6rem 0}
caption{text-align:left;color:var(--mute);font-size:.78rem;padding-bottom:.4rem}
th,td{padding:.3rem .5rem;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}
td{font-variant-numeric:tabular-nums}
details summary{cursor:pointer;font-weight:800;color:var(--accent);font-size:.86rem}
#tip{position:fixed;z-index:50;pointer-events:none;background:var(--ink);color:var(--bg);font-size:.78rem;line-height:1.35;padding:.4rem .6rem;border-radius:10px;opacity:0;transition:opacity .12s;max-width:15rem;box-shadow:0 6px 20px -8px #000}
#tip b{color:var(--gold)}
footer{margin:4rem 0 0;padding:1.4rem 0 2.4rem;border-top:3px solid var(--ink);font-size:.8rem;color:var(--mute)}
.spider{cursor:pointer}
@keyframes zz{0%{opacity:0;transform:translate(0,0) scale(.6)}30%{opacity:1}100%{opacity:0;transform:translate(14px,-34px) scale(1.2)}}
.z{animation:zz 2.2s ease-out infinite;transform-box:fill-box}
@keyframes wob{0%,100%{transform:rotate(0)}25%{transform:rotate(-12deg)}75%{transform:rotate(12deg)}}
.wiggle{animation:wob .5s ease-in-out 2;transform-box:fill-box;transform-origin:50% 50%}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
"""


SITE = "https://nanobotco.github.io/yandex-bots/"
CARD_ALT = {
    "en": "The Crawler Went Quiet: hourly bot traffic, Yandex bots falling after the strikes while the rest of Russia stays level",
    "th": "เมื่อแมงมุมของยานเดกซ์หลับ: ทราฟฟิกบอตรายชั่วโมง บอตของยานเดกซ์ลดลงหลังการโจมตี ส่วนรัสเซียที่เหลือคงที่",
}


def page(L):
    t = T[L]
    base = "" if L == "en" else "../"
    nav = "".join(f'<a href="#{a}">{b}</a>' for a, b in t["nav"])
    slab = "".join(f'<button type="button"><b>{v}</b><span>{a}</span><i>{b}</i></button>' for v, a, b in t["slab"])
    rows = "".join(
        f"<tr><td>{en if L == 'en' else th}</td><td>{pct(b)}</td><td>{pct(h)}</td></tr>" for k, en, th, b, h in TABLE)
    cfg = {"lang": L, "base": base, "strikes": t["strikes"], "tip_bots": t["tip_bots"], "tip_hum": t["tip_hum"],
           "tip_base": t["tip_base"], "axis_base": t["axis_base"], "wf": t["wf"],
           "wfv": [100, N["wf_y"], N["wf_yc"], N["wf_rest"], 100 + N["wf_ru"]],
           "names": {n["key"]: (n["en"] if L == "en" else n["th"]) for n in D["nets"]},
           "chg": {k: round(b * 100, 1) for k, en, th, b, h in TABLE}}
    P = lambda xs: "".join(f"<p>{x}</p>" for x in xs)
    legend = (f'<div class="legend"><span><svg viewBox="0 0 28 10"><path d="M1 5h26" stroke="var(--accent)" stroke-width="2.5" fill="none"/></svg>{t["legend_bots"]}</span>'
              f'<span><svg viewBox="0 0 28 10"><path d="M1 5h26" stroke="var(--mute)" stroke-width="2" stroke-dasharray="4 3" fill="none"/></svg>{t["legend_hum"]}</span></div>')
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{html.escape(t['desc'])}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{t['title']}">
<meta property="og:title" content="{t['title']}">
<meta property="og:description" content="{html.escape(t['desc'])}">
<meta property="og:url" content="{SITE}{'' if L == 'en' else 'th/'}">
<meta property="og:image" content="{SITE}{'' if L == 'en' else 'th/'}card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(CARD_ALT[L])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}{'' if L == 'en' else 'th/'}card.jpg">
<link rel="icon" href="{base}icon.svg">
<link rel="alternate" hreflang="en" href="https://nanobotco.github.io/yandex-bots/">
<link rel="alternate" hreflang="th" href="https://nanobotco.github.io/yandex-bots/th/">
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="#top">{t['title']}</a>
<nav>{nav}</nav>
<a class="langsw" href="{t['other']}" hreflang="{'th' if L == 'en' else 'en'}">{t['other_label']}</a>
</div></header>
<section class="hero" id="top"><div class="wrap">
<span class="kicker">{t['kicker']}</span>
<h1>{t['title']}</h1>
<p class="lede">{t['lede']}</p>
<p class="hint">{t['hint']}</p>
<div class="chart" id="hero-chart" role="img" aria-label="{html.escape(t['desc'])}"></div>
</div></section>
<main class="wrap">
<div class="slab">{slab}</div>

<h2 id="hours">{t['h_hours']}</h2>
<div class="steps">{P(t['p_hours'])}</div>

<h2 id="networks">{t['h_net']}</h2>
<p>{t['p_net']}</p>
{legend}
<div class="grid10" id="grid10"></div>
<p class="hint" style="color:var(--mute)">{t['p_net2']}</p>
<details><summary>{t['tbl_head'][0]} · {t['tbl_head'][1]} · {t['tbl_head'][2]}</summary>
<table><caption>{t['tbl_cap']}</caption><thead><tr><th>{t['tbl_head'][0]}</th><th>{t['tbl_head'][1]}</th><th>{t['tbl_head'][2]}</th></tr></thead><tbody>{rows}</tbody></table>
</details>

<h2 id="russia">{t['h_ru']}</h2>
<p>{t['p_ru']}</p>
<div class="box"><div class="chart" id="share-chart"></div></div>

<h2 id="sum">{t['h_sum']}</h2>
<p>{t['p_sum']}</p>
<div class="box"><div class="chart" id="wf-chart"></div></div>
<div class="eq">{t['eq']}</div>

<h2 id="bots">{t['h_bots']}</h2>
{P(t['p_bots'])}

<h2 id="data">{t['h_data']}</h2>
{P(x.replace('{base}', base) for x in t['p_data'])}
<footer>{t['foot']}</footer>
</main>
<div id="tip" role="status" aria-live="polite"></div>
<script>window.YB={json.dumps(cfg, ensure_ascii=False)}</script>
<script src="{base}yb.js" defer></script>
</body>
</html>
"""


for L, path in (("en", "docs/index.html"), ("th", "docs/th/index.html")):
    open(os.path.join(ROOT, path), "w").write(page(L))
for k in ("y", "yc", "ru", "rest", "explained", "wf_y", "wf_yc", "wf_rest", "wf_ru", "step8", "yh", "ys4", "ys11", "yown"):
    print(f"{k:10} {N[k]:.4f}")
