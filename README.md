# The Crawler Went Quiet · เมื่อแมงมุมของยานเดกซ์หลับ

Drone strikes on Yandex data centers, 8–11 October 2026, read hour by hour from Cloudflare Radar.
English and Thai. https://nanobotco.github.io/yandex-bots/

- `tools/data.py` pulls the Radar series into `docs/data.json` (token: `token get CLOUDFLARE_RADAR_TOKEN`).
- `tools/build.py` computes the numbers and writes `docs/index.html` and `docs/th/index.html`.
- `docs/yb.js` draws the charts.

Data: Cloudflare Radar, CC BY-NC 4.0. Text and drawings: CC BY 4.0. Code: MIT.
