// The Crawler Went Quiet — every chart on the page, drawn by hand-wobbled math from data.json.
(() => {
  const C = window.YB, NS = "http://www.w3.org/2000/svg";
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const tip = document.getElementById("tip");
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const el = (tag, at = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in at) e.setAttribute(k, at[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const rng = (seed) => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  // a pen line: each vertex nudged a little, joined with soft curves
  const wob = (pts, amp, seed) => {
    const r = rng(seed);
    const p = pts.map(([x, y]) => [x + (r() - .5) * amp, y + (r() - .5) * amp]);
    let d = `M${p[0][0].toFixed(1)} ${p[0][1].toFixed(1)}`;
    for (let i = 1; i < p.length; i++) {
      const [x0, y0] = p[i - 1], [x1, y1] = p[i];
      d += ` Q${x0.toFixed(1)} ${y0.toFixed(1)} ${((x0 + x1) / 2).toFixed(1)} ${((y0 + y1) / 2).toFixed(1)}`;
    }
    const [xl, yl] = p[p.length - 1];
    return d + ` L${xl.toFixed(1)} ${yl.toFixed(1)}`;
  };
  const seg = (x0, y0, x1, y1, n = 8) => Array.from({ length: n + 1 }, (_, i) => [x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n]);
  const fmtHour = (t) => {
    const d = new Date(t);
    const day = d.toLocaleDateString(C.lang === "th" ? "th-TH" : "en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
    return `${day} ${String(d.getUTCHours()).padStart(2, "0")}:00 UTC`;
  };
  const fmtDay = (t) => new Date(t).toLocaleDateString(C.lang === "th" ? "th-TH" : "en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
  const showTip = (html, x, y) => {
    tip.innerHTML = html; tip.style.opacity = 1;
    const w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.min(innerWidth - w - 8, Math.max(8, x + 14)) + "px";
    tip.style.top = Math.max(8, y - h - 14) + "px";
  };
  const hideTip = () => (tip.style.opacity = 0);
  const wiggle = (node) => { node.classList.remove("wiggle"); void node.getBBox?.(); node.classList.add("wiggle"); };

  fetch(C.base + "data.json").then((r) => r.json()).then((D) => {
    const T = D.hours.map((h) => Date.parse(h));
    const net = Object.fromEntries(D.nets.map((n) => [n.key, n]));
    let seed = 7;
    const draws = [];
    const redraw = () => draws.forEach((f) => f());

    // ---------------------------------------------------------------- hero
    const hero = document.getElementById("hero-chart");
    const h0 = Date.parse("2026-09-28T00:00:00Z"), h1 = Date.parse("2026-10-12T00:00:00Z");
    const i0 = T.findIndex((t) => t >= h0), i1 = T.findIndex((t) => t >= h1 - 1) + 1 || T.length;
    let pick = i1 - 1, first = true;
    const drawHero = () => {
      hero.innerHTML = "";
      const W = Math.max(320, hero.clientWidth), H = Math.round(Math.min(420, Math.max(250, W * .42)));
      const narrow = W < 560, m = { l: 34, r: 14, t: narrow ? 58 : 40, b: 30 };
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, hero);
      const X = (t) => m.l + (t - h0) / (h1 - h0) * (W - m.l - m.r);
      const Y = (v) => m.t + (1 - Math.min(v, 150) / 150) * (H - m.t - m.b);
      const ink = "#fbf2e8", mute = "#bcb0cc", grid = "#3a2f55", hot = "#ff7a3d", gold = "#ffc53d";
      for (const v of [0, 50, 100, 150]) {
        el("path", { d: wob(seg(m.l, Y(v), W - m.r, Y(v), 30), .8, seed + v), stroke: grid, "stroke-width": v === 100 ? 1.6 : 1, fill: "none", "stroke-dasharray": v === 100 ? "6 5" : "" }, svg);
        el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end", fill: mute, "font-size": 11 }, svg).textContent = v;
      }
      el("text", { x: W - m.r, y: Y(100) - 6, "text-anchor": "end", fill: mute, "font-size": 11 }, svg).textContent = C.axis_base;
      for (let t = h0; t <= h1; t += (narrow ? 4 : 2) * 864e5) {
        el("text", { x: X(t), y: H - 8, "text-anchor": "middle", fill: mute, "font-size": 11 }, svg).textContent = fmtDay(t);
      }
      C.strikes.forEach(([t, name], k) => {
        const x = X(Date.parse(t));
        el("path", { d: wob(seg(x, narrow ? m.t - 36 + k * 14 : m.t - 14, x, H - m.b, 12), 1.6, seed + 40 + k), stroke: gold, "stroke-width": 1.5, fill: "none", "stroke-dasharray": "3 4" }, svg);
        const lab = el("text", { x: x - 4, y: narrow ? m.t - 40 + k * 14 : (k === 1 ? m.t - 4 : m.t - 20), "text-anchor": "end", fill: gold, "font-size": 12, "font-weight": 800 }, svg);
        lab.textContent = "✶ " + name;
      });
      const pts = (key) => T.slice(i0, i1).map((t, j) => [X(t), Y(net[key][key === "yandex" ? "bots" : "bots"][i0 + j])]);
      const hum = T.slice(i0, i1).map((t, j) => [X(t), Y(net.yandex.humans[i0 + j])]);
      el("path", { d: wob(hum, 1.2, seed + 3), stroke: mute, "stroke-width": 1.6, fill: "none", "stroke-dasharray": "5 4", opacity: .8 }, svg);
      const bp = pts("yandex");
      el("path", { d: wob(bp, 2.4, seed + 9), stroke: hot, "stroke-width": 1.2, fill: "none", opacity: .45 }, svg);
      const line = el("path", { d: wob(bp, 1.2, seed + 5), stroke: hot, "stroke-width": 2.6, fill: "none", "stroke-linecap": "round" }, svg);
      if (first && !still) {
        const L = line.getTotalLength();
        line.style.strokeDasharray = L; line.style.strokeDashoffset = L;
        line.getBoundingClientRect();
        line.style.transition = "stroke-dashoffset 2.6s ease-in-out";
        line.style.strokeDashoffset = 0;
      }
      first = false;
      // crosshair + spider
      const cross = el("path", { stroke: ink, "stroke-width": 1, opacity: .35, fill: "none" }, svg);
      const sp = el("g", { class: "spider", tabindex: 0, role: "button", "aria-label": "spider" }, svg);
      const thread = el("path", { stroke: ink, "stroke-width": .8, opacity: .6, fill: "none" }, svg);
      svg.insertBefore(thread, sp);
      const body = el("g", {}, sp);
      for (let s = -1; s <= 1; s += 2) for (let k = 0; k < 4; k++) {
        const a = (-50 + k * 33) * Math.PI / 180;
        const kx = s * (7 + 9 * Math.cos(a)), ky = -2 + 9 * Math.sin(a);
        el("path", { d: wob([[s * 3, 0], [kx, ky - 5], [s * (10 + 6 * Math.cos(a)), ky + 6]], .6, seed + k * 3 + s), stroke: ink, "stroke-width": 1.5, fill: "none", "stroke-linecap": "round" }, body);
      }
      el("ellipse", { cx: 0, cy: 0, rx: 7, ry: 8, fill: "#2a2142", stroke: ink, "stroke-width": 1.5 }, body);
      el("circle", { cx: 0, cy: -9, r: 4.5, fill: "#2a2142", stroke: ink, "stroke-width": 1.5 }, body);
      const eyes = el("g", {}, body);
      const zs = el("g", {}, sp);
      const place = (i) => {
        pick = i;
        const t = T[i], v = net.yandex.bots[i], x = X(t), y = Y(v);
        cross.setAttribute("d", `M${x} ${m.t - 6}V${H - m.b}`);
        thread.setAttribute("d", `M${x} ${m.t - 6}V${y - 12}`);
        sp.setAttribute("transform", `translate(${x.toFixed(1)} ${(y - 2).toFixed(1)})`);
        const asleep = v < 20;
        eyes.innerHTML = asleep
          ? `<path d="M-3 -9.5q1.2 1.2 2.2 0M.8 -9.5q1.2 1.2 2.2 0" stroke="${ink}" stroke-width="1.1" fill="none"/>`
          : `<circle cx="-1.6" cy="-9.5" r="1.1" fill="${ink}"/><circle cx="1.6" cy="-9.5" r="1.1" fill="${ink}"/>`;
        zs.innerHTML = asleep ? `<text class="z" x="8" y="-14" fill="${gold}" font-size="12" font-weight="800">z</text><text class="z" x="13" y="-20" fill="${gold}" font-size="9" font-weight="800" style="animation-delay:1.1s">z</text>` : "";
        return { x, v, h: net.yandex.humans[i] };
      };
      place(pick);
      const at = (ev) => {
        const r = svg.getBoundingClientRect();
        const t = h0 + ((ev.clientX - r.left) / r.width * W - m.l) / (W - m.l - m.r) * (h1 - h0);
        let i = Math.round((t - T[0]) / 36e5);
        i = Math.max(i0, Math.min(i1 - 1, i));
        const p = place(i);
        showTip(`${fmtHour(T[i])}<br><b>${C.tip_bots} ${p.v.toFixed(0)}</b> · ${C.tip_hum} ${p.h.toFixed(0)}<br><span style="opacity:.75">${C.tip_base}</span>`, ev.clientX, ev.clientY);
      };
      svg.addEventListener("pointermove", at);
      svg.addEventListener("pointerdown", at);
      svg.addEventListener("pointerleave", hideTip);
      const poke = (e) => { e.stopPropagation(); wiggle(body); zs.innerHTML = `<text x="9" y="-16" fill="${gold}" font-size="15" font-weight="900">!</text>`; setTimeout(() => place(pick), 900); };
      sp.addEventListener("click", poke);
      sp.addEventListener("keydown", (e) => (e.key === "Enter" || e.key === " ") && poke(e));
    };
    draws.push(drawHero);

    // ---------------------------------------------------------------- ten panels
    const grid = document.getElementById("grid10");
    const g0 = T[0], g1 = T[T.length - 1];
    const panels = D.nets.map((n, k) => {
      const b = document.createElement("button");
      b.className = "panel"; b.type = "button";
      const c = C.chg[n.key];
      b.innerHTML = `<div class="nm"><span>${C.names[n.key]}</span><em>${c > 0 ? "+" : ""}${c.toFixed(0).replace("-", "−")}%</em></div>`;
      grid.appendChild(b);
      let s = 100 + k * 11;
      const draw = () => {
        b.querySelector("svg")?.remove();
        const W = 220, H = 104, m = { l: 4, r: 4, t: 6, b: 6 };
        const svg = el("svg", { viewBox: `0 0 ${W} ${H}` }, b);
        const X = (t) => m.l + (t - g0) / (g1 - g0) * (W - m.l - m.r);
        const Y = (v) => m.t + (1 - Math.min(v, 250) / 250) * (H - m.t - m.b);
        const s0 = X(Date.parse("2026-10-08T00:00:00Z"));
        el("rect", { x: s0, y: m.t, width: W - m.r - s0, height: H - m.t - m.b, fill: css("--gold"), opacity: .14, rx: 4 }, svg);
        el("path", { d: wob(seg(m.l, Y(100), W - m.r, Y(100), 12), .6, s), stroke: css("--grid"), "stroke-width": 1.2, fill: "none", "stroke-dasharray": "4 4" }, svg);
        const step = 3;
        const ph = [], pb = [];
        for (let i = 0; i < T.length; i += step) { ph.push([X(T[i]), Y(n.humans[i])]); pb.push([X(T[i]), Y(n.bots[i])]); }
        el("path", { d: wob(ph, .9, s + 1), stroke: css("--mute"), "stroke-width": 1.2, fill: "none", "stroke-dasharray": "3 3", opacity: .8 }, svg);
        el("path", { d: wob(pb, .9, s + 2), stroke: css("--accent"), "stroke-width": 2, fill: "none", "stroke-linecap": "round" }, svg);
        svg.addEventListener("pointermove", (ev) => {
          const r = svg.getBoundingClientRect();
          const t = g0 + ((ev.clientX - r.left) / r.width * W - m.l) / (W - m.l - m.r) * (g1 - g0);
          const i = Math.max(0, Math.min(T.length - 1, Math.round((t - T[0]) / 36e5)));
          showTip(`<b>${C.names[n.key]}</b><br>${fmtHour(T[i])}<br>${C.tip_bots} ${n.bots[i].toFixed(0)} · ${C.tip_hum} ${n.humans[i].toFixed(0)}`, ev.clientX, ev.clientY);
        });
        svg.addEventListener("pointerleave", hideTip);
      };
      b.addEventListener("click", () => { s += 97; draw(); wiggle(b.querySelector("svg")); });
      return draw;
    });
    draws.push(() => panels.forEach((f) => f()));

    // ---------------------------------------------------------------- Yandex share of Russia's bots
    const share = document.getElementById("share-chart");
    const drawShare = () => {
      share.innerHTML = "";
      const W = Math.max(300, share.clientWidth), H = 230, m = { l: 30, r: 6, t: 22, b: 28 };
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, share);
      const days = D.ruTop.map((d) => ({ day: d.day, v: (d.top.find((x) => x.asn === 13238) || {}).pct || 0 }));
      const bw = (W - m.l - m.r) / days.length;
      const Y = (v) => m.t + (1 - v / 12) * (H - m.t - m.b);
      for (const v of [0, 4, 8, 12]) {
        el("path", { d: wob(seg(m.l, Y(v), W - m.r, Y(v), 16), .6, seed + v), stroke: css("--grid"), "stroke-width": 1, fill: "none" }, svg);
        el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end", fill: css("--mute"), "font-size": 11 }, svg).textContent = v + "%";
      }
      days.forEach((d, k) => {
        const x = m.l + k * bw + 2, w = bw - 4, y = Y(d.v), y0 = Y(0);
        const r = Math.min(4, w / 2, y0 - y);
        const g = el("g", { style: "cursor:pointer" }, svg);
        el("path", { d: `M${x} ${y0}V${y + r}Q${x} ${y} ${x + r} ${y}H${x + w - r}Q${x + w} ${y} ${x + w} ${y + r}V${y0}Z`, fill: d.day >= "2026-10-08" ? css("--accent") : css("--mute"), opacity: d.day >= "2026-10-08" ? 1 : .55 }, g);
        el("rect", { x: x - 2, y: m.t, width: bw, height: H - m.t - m.b, fill: "transparent" }, g);
        if (k % 2 === 0 || k === days.length - 1)
          el("text", { x: x + w / 2, y: H - 8, "text-anchor": "middle", fill: css("--mute"), "font-size": 10.5 }, svg).textContent = fmtDay(d.day + "T00:00:00Z");
        if (k === 0 || k === days.length - 1 || d.day === "2026-10-04")
          el("text", { x: x + w / 2, y: y - 6, "text-anchor": "middle", fill: css("--ink"), "font-size": 11, "font-weight": 800 }, svg).textContent = d.v.toFixed(1) + "%";
        const tipIt = (ev) => showTip(`${fmtDay(d.day + "T00:00:00Z")}<br><b>${d.v.toFixed(2)}%</b>`, ev.clientX, ev.clientY);
        g.addEventListener("pointermove", tipIt);
        g.addEventListener("pointerleave", hideTip);
        g.addEventListener("click", (ev) => { tipIt(ev); wiggle(g); });
      });
    };
    draws.push(drawShare);

    // ---------------------------------------------------------------- waterfall
    const wf = document.getElementById("wf-chart");
    const drawWf = () => {
      wf.innerHTML = "";
      const W = Math.max(300, wf.clientWidth), H = 260, m = { l: 30, r: 6, t: 26, b: 34 };
      const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H }, wf);
      const Y = (v) => m.t + (1 - v / 105) * (H - m.t - m.b);
      for (const v of [0, 25, 50, 75, 100]) {
        el("path", { d: wob(seg(m.l, Y(v), W - m.r, Y(v), 16), .6, seed + v), stroke: css("--grid"), "stroke-width": 1, fill: "none" }, svg);
        el("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end", fill: css("--mute"), "font-size": 11 }, svg).textContent = v;
      }
      const bw = (W - m.l - m.r) / C.wf.length;
      let run = 0;
      C.wf.forEach(([name, kind], k) => {
        const v = C.wfv[k];
        let a, b, fill, lab;
        if (kind === "total") { a = 0; b = v; run = v; fill = css("--ink"); lab = v.toFixed(1); }
        else { a = run; b = run + v; run = b; fill = v < 0 ? css("--accent") : css("--mute"); lab = (v > 0 ? "+" : "−") + Math.abs(v).toFixed(2); }
        const lo = Math.min(a, b), hi = Math.max(a, b);
        const x = m.l + k * bw + bw * .18, w = bw * .64;
        const hgt = Math.max(2.5, Y(lo) - Y(hi));
        const g = el("g", { style: "cursor:pointer" }, svg);
        el("rect", { x, y: Y(hi), width: w, height: hgt, rx: 4, fill }, g);
        el("text", { x: x + w / 2, y: Y(hi) - 7, "text-anchor": "middle", fill: css("--ink"), "font-size": 12, "font-weight": 800 }, g).textContent = lab;
        el("text", { x: x + w / 2, y: H - 12, "text-anchor": "middle", fill: css("--mute"), "font-size": W < 420 ? 9.5 : 11.5 }, svg).textContent = name;
        g.addEventListener("click", () => wiggle(g));
      });
    };
    draws.push(drawWf);

    document.querySelectorAll(".slab button").forEach((b) => b.addEventListener("click", () => { seed += 13; drawHero(); }));
    redraw();
    let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(redraw, 150); });
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redraw);
  });
})();
