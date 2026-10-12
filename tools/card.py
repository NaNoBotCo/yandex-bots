#!/usr/bin/env python3
"""Share cards, 1200x630 JPEG: docs/card.jpg (English) and docs/th/card.jpg (Thai).

Drawn from docs/data.json with headless Chrome: the page's palette and type, a title, and the
hourly bot-traffic index for Yandex and for all of Russia. `python3 tools/card.py`
"""
import json, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
D = json.loads((ROOT / "docs" / "data.json").read_text())
H = D["hours"]
NET = {n["key"]: n for n in D["nets"]}
b0, b1 = D["baseline"]
base_idx = [i for i, t in enumerate(H) if b0 <= t[:10] <= b1]


def index(key):
    v = NET[key]["bots"]
    m = sum(v[i] for i in base_idx) / len(base_idx)
    return [x / m * 100 for x in v]


W, HT, X0, Y0, PW, PH, TOP = 1200, 630, 72, 400, 1056, 180, 160  # chart box: x 72..1128, y 400..580 (index 0..TOP)


def path(vals):
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = X0 + PW * i / (n - 1)
        y = Y0 + PH - PH * min(v, TOP) / TOP
        pts.append(f"{x:.1f},{y:.1f}")
    return "M" + " L".join(pts)


def xat(day):
    i = next(i for i, t in enumerate(H) if t.startswith(day))
    return X0 + PW * i / (len(H) - 1)


LANG = {
    "en": dict(lang="en", kicker="CLOUDFLARE RADAR · 8–11 OCTOBER 2026", title="The Crawler<br>Went Quiet",
               a="Yandex bots", b="Rest of Russia", out=ROOT / "docs" / "card.jpg", cls="en"),
    "th": dict(lang="th", kicker="CLOUDFLARE RADAR · 8–11 ตุลาคม 2026", title="เมื่อแมงมุมของ<br>ยานเดกซ์หลับ",
               a="บอตของยานเดกซ์", b="รัสเซียส่วนที่เหลือ", out=ROOT / "docs" / "th" / "card.jpg", cls="th"),
}


def page(L):
    yb, ru = path(index("yandex")), path(index("ru"))
    strikes = "".join(
        f'<line x1="{xat(d):.1f}" x2="{xat(d):.1f}" y1="{Y0 - 10}" y2="{Y0 + PH}" stroke="#ffc53d" stroke-width="2" stroke-dasharray="5 5"/>'
        for d in ("2026-10-08", "2026-10-09", "2026-10-11"))
    ybase = Y0 + PH - PH * 100 / TOP
    return f"""<!doctype html><html lang="{L['lang']}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:{W}px;height:{HT}px;overflow:hidden;background:#16112a;color:#fbf2e8;position:relative;
 font-family:"Avenir Next","Noto Sans Thai",Thonburi,system-ui,sans-serif}}
.bar{{position:absolute;left:0;right:0;top:0;height:8px;background:#ff7a3d}}
.k{{position:absolute;left:72px;top:46px;font:800 22px/1 "Avenir Next Condensed","Noto Sans Thai",Thonburi,sans-serif;letter-spacing:.3em;color:#ffc53d}}
.th .k{{letter-spacing:.12em;font-size:24px}}
h1{{position:absolute;left:72px;top:88px;font:800 128px/.9 "Avenir Next Condensed",Impact,sans-serif;text-transform:uppercase;letter-spacing:.005em}}
.th h1{{font:700 98px/1.12 Thonburi,"Noto Sans Thai",sans-serif;text-transform:none;top:84px}}
.lg{{position:absolute;right:72px;top:96px;font:700 24px/1.9 "Avenir Next","Noto Sans Thai",Thonburi,sans-serif;text-align:right}}
.lg i{{display:inline-block;width:34px;height:5px;margin-right:12px;vertical-align:middle;border-radius:3px}}
svg{{position:absolute;left:0;top:0}}
</style></head><body class="{L['cls']}">
<div class="bar"></div><div class="k">{L['kicker']}</div><h1>{L['title']}</h1>
<div class="lg"><div><i style="background:#ff7a3d"></i>{L['a']}</div><div><i style="background:#bcb0cc"></i>{L['b']}</div></div>
<svg width="{W}" height="{HT}" viewBox="0 0 {W} {HT}">
<line x1="{X0}" x2="{X0 + PW}" y1="{ybase:.1f}" y2="{ybase:.1f}" stroke="#3a2f55" stroke-width="2" stroke-dasharray="3 5"/>
{strikes}
<path d="{ru}" fill="none" stroke="#bcb0cc" stroke-width="2.5" stroke-linejoin="round" opacity=".85"/>
<path d="{yb}" fill="none" stroke="#ff7a3d" stroke-width="4" stroke-linejoin="round"/>
</svg></body></html>"""


def main():
    from PIL import Image
    for k, L in LANG.items():
        with tempfile.TemporaryDirectory() as tmp:
            p, shot = Path(tmp) / "c.html", Path(tmp) / "c.png"
            p.write_text(page(L), encoding="utf-8")
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                            "--force-device-scale-factor=1", f"--window-size={W},{HT}",
                            f"--screenshot={shot}", p.as_uri()], check=True, capture_output=True, timeout=60)
            Image.open(shot).convert("RGB").crop((0, 0, W, HT)).save(L["out"], "JPEG", quality=88, optimize=True)
        print(L["out"])


if __name__ == "__main__":
    main()
