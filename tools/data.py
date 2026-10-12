#!/usr/bin/env python3
"""Bake docs/data.json from Cloudflare Radar. Token: ~/.claude/bin/token get CLOUDFLARE_RADAR_TOKEN."""
import json, os, subprocess, time, urllib.parse, urllib.request

TOKEN = subprocess.run([os.path.expanduser("~/.claude/bin/token"), "get", "CLOUDFLARE_RADAR_TOKEN"],
                       capture_output=True, text=True).stdout.strip()
API = "https://api.cloudflare.com/client/v4/radar/http"
START, END = "2026-09-21T00:00:00Z", "2026-10-12T00:00:00Z"
BASE = ("2026-09-21", "2026-10-07")          # baseline days, before the first strike
NETS = [
    ("yandex", "Yandex", "ยานเดกซ์", {"asn": "13238"}),
    ("ycloud", "Yandex Cloud", "ยานเดกซ์คลาวด์", {"asn": "200350"}),
    ("rt", "Rostelecom", "รอสเตเลคอม", {"asn": "12389"}),
    ("mts", "MTS", "MTS", {"asn": "8359"}),
    ("megafon", "MegaFon", "เมกะฟอน", {"asn": "31133"}),
    ("beeline", "Beeline", "บีไลน์", {"asn": "8402"}),
    ("selectel", "Selectel", "เซเลกเทล", {"asn": "49505"}),
    ("timeweb", "Timeweb", "ไทม์เว็บ", {"asn": "9123"}),
    ("vk", "VK", "VK", {"asn": "47764"}),
    ("ru", "All of Russia", "ทั้งรัสเซีย", {"location": "RU"}),
]

def get(path, params, start=START, end=END):
    q = urllib.parse.urlencode({**params, "dateStart": start, "dateEnd": end, "format": "json"})
    for i in range(4):
        try:
            req = urllib.request.Request(f"{API}/{path}?{q}", headers={"Authorization": f"Bearer {TOKEN}"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if r.get("success"): return r["result"]
        except Exception as e:
            err = e
        time.sleep(2 + i * 3)
    raise SystemExit(f"radar failed: {path} {params}")

def index(ts, vals):
    vals = [float(v) for v in vals]
    base = [v for t, v in zip(ts, vals) if BASE[0] <= t[:10] < BASE[1]]
    m = sum(base) / len(base)
    return [round(v / m * 100, 2) for v in vals]

out = {"start": START, "end": END, "baseline": BASE, "nets": [], "pulled": time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())}
ts = None
for key, en, th, p in NETS:
    b = get("timeseries", {**p, "botClass": "LIKELY_AUTOMATED", "aggInterval": "1h", "normalization": "MIN0_MAX"})["serie_0"]
    h = get("timeseries", {**p, "botClass": "LIKELY_HUMAN", "aggInterval": "1h", "normalization": "MIN0_MAX"})["serie_0"]
    mix = get("timeseries_groups/bot_class", {**p, "aggInterval": "1d"})["serie_0"]
    ts = ts or b["timestamps"]
    assert b["timestamps"] == ts and h["timestamps"] == ts, key
    out["nets"].append({"key": key, "en": en, "th": th, "q": p,
                        "bots": index(ts, b["values"]), "humans": index(ts, h["values"]),
                        "botsMax": [round(float(v), 2) for v in b["values"]],
                        "botShare": {"days": [t[:10] for t in mix["timestamps"]], "pct": [round(float(v), 2) for v in mix["bot"]]}})
    print("ok", key)
out["hours"] = ts
# who sends Russia's bots, day by day
days = []
d = time.strptime("2026-09-28", "%Y-%m-%d")
t0 = time.mktime(d)
for i in range(14):
    a = time.strftime("%Y-%m-%d", time.localtime(t0 + i * 86400 + 7200))
    b = time.strftime("%Y-%m-%d", time.localtime(t0 + (i + 1) * 86400 + 7200))
    top = get("top/ases", {"botClass": "LIKELY_AUTOMATED", "location": "RU", "limit": "25"}, f"{a}T00:00:00Z", f"{b}T00:00:00Z")["top_0"]
    days.append({"day": a, "top": [{"asn": x["clientASN"], "name": x["clientASName"], "pct": round(float(x["value"]), 3)} for x in top]})
    print("top", a)
out["ruTop"] = days
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "docs", "data.json"), "w"), separators=(",", ":"))
print("wrote docs/data.json")
