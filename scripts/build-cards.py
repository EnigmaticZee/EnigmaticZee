#!/usr/bin/env python3
"""Generates the profile cards in assets/:

  now-shipping.svg  – PawsOff card with a paw tapping a locked keyboard
  process.svg       – observe → sketch → design → build → ship (scripts/process_card.py)
  toolkit.svg       – the toolkit as a Figma-style canvas with a live cursor

Everything is self-contained (no external requests), so nothing can rate-limit.
Pass the PawsOff icon path as the first argument to embed it.
"""
import base64, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import process_card

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Courier New', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
C = dict(bg="#0e0c14", bar="#16131f", panel="#13101b", border="#2c2740", grid="#241f33",
         text="#ece9f5", muted="#8a84a3", dim="#4d4766", violet="#a78bfa", violet2="#8b6cf0",
         amber="#f2c14e", mint="#6ee7b7", select="#5b9dff")
W = 842


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def window(h, title, right=""):
    return f'''<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>
  <path d="M1 13a12 12 0 0 1 12-12h{W-26}a12 12 0 0 1 12 12v25H1z" fill="{C["bar"]}"/>
  <line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{C["border"]}"/>
  <circle cx="24" cy="19.5" r="6" fill="#ff5f56"/><circle cx="44" cy="19.5" r="6" fill="#ffbd2e"/><circle cx="64" cy="19.5" r="6" fill="#27c93f"/>
  <text x="{W/2}" y="24" fill="{C["muted"]}" font-family="{MONO}" font-size="12" text-anchor="middle">{esc(title)}</text>
  <text x="{W-20}" y="24" fill="{C["dim"]}" font-family="{MONO}" font-size="11" text-anchor="end">{esc(right)}</text>'''


def svg(h, label, body, defs=""):
    return f'''<svg viewBox="0 0 {W} {h}" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" role="img" aria-label="{esc(label)}">
  <defs>
    <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.8" fill="{C["grid"]}"/></pattern>
    {defs}
  </defs>
  {body}
</svg>
'''


# ---------------------------------------------------------------- now shipping
def now_shipping(icon_path):
    H = 190
    icon = ""
    if icon_path:
        from PIL import Image
        im = Image.open(icon_path).convert("RGBA").resize((176, 176), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        icon = f'<image x="26" y="60" width="88" height="88" href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}"/>'

    # keyboard: 3 rows of keys on the right
    kx, ky, k, gap = 514, 56, 24, 5
    rows = [10, 9, 8]
    keys = []
    for r, n in enumerate(rows):
        off = r * 12
        for i in range(n):
            x = kx + off + i * (k + gap)
            keys.append(f'<rect x="{x}" y="{ky + r*(k+gap)}" width="{k}" height="{k}" rx="5" fill="{C["bar"]}" stroke="{C["border"]}"/>')
    # space bar
    keys.append(f'<rect x="{kx+60}" y="{ky+3*(k+gap)}" width="{k*6+gap*5}" height="{k}" rx="5" fill="{C["bar"]}" stroke="{C["border"]}"/>')
    keys_s = "\n    ".join(keys)

    # paw that hops across the keys; each press flashes a red "blocked" ring, never a keypress
    hops = [(kx + 40, ky + 18), (kx + 130, ky + 50), (kx + 220, ky + 20), (kx + 170, ky + 84), (kx + 270, ky + 52)]
    vals = ";".join(f"{x} {y}" for x, y in hops + [hops[0]])
    n = len(hops)
    kt = ";".join(f"{i/n:.3f}" for i in range(n + 1))
    paw = f'''<g opacity="0.95">
      <animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="{";".join(["0.5 0 0.3 1"]*n)}"/>
      <circle r="16" fill="none" stroke="#ff6b6b" stroke-width="2" opacity="0">
        <animate attributeName="opacity" values="0;0;0.9;0" keyTimes="0;0.55;0.7;1" dur="1.2s" repeatCount="indefinite"/>
        <animate attributeName="r" values="10;10;22;26" keyTimes="0;0.55;0.8;1" dur="1.2s" repeatCount="indefinite"/>
      </circle>
      <ellipse cx="0" cy="4" rx="8" ry="7" fill="{C["amber"]}"/>
      <circle cx="-8" cy="-6" r="3.4" fill="{C["amber"]}"/><circle cx="-3" cy="-11" r="3.4" fill="{C["amber"]}"/>
      <circle cx="3" cy="-11" r="3.4" fill="{C["amber"]}"/><circle cx="8" cy="-6" r="3.4" fill="{C["amber"]}"/>
    </g>'''

    lock = f'''<g transform="translate(790 148)">
      <rect x="-15" y="-4" width="30" height="22" rx="5" fill="{C["violet"]}"/>
      <path d="M-8 -4v-6a8 8 0 0 1 16 0v6" stroke="{C["violet"]}" stroke-width="3.5" fill="none"/>
      <circle cx="0" cy="7" r="3" fill="{C["bg"]}"/>
      <circle r="24" cy="4" fill="none" stroke="{C["violet"]}" stroke-width="1.5">
        <animate attributeName="r" values="18;30" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.6;0" dur="2s" repeatCount="indefinite"/>
      </circle>
    </g>'''

    body = f'''{window(H, "now-shipping — paws-off", "v2")}
  <rect x="490" y="39" width="{W-491}" height="{H-40}" fill="url(#dots)"/>
  <line x1="490" y1="38" x2="490" y2="{H-1}" stroke="{C["border"]}"/>
  {icon}
  <text x="134" y="84" fill="{C["text"]}" font-family="{SANS}" font-size="24" font-weight="700">Paws Off</text>
  <text x="134" y="110" fill="{C["muted"]}" font-family="{SANS}" font-size="14">Pause your keyboard with one click.</text>
  <text x="134" y="130" fill="{C["muted"]}" font-family="{SANS}" font-size="14">Wipe it down, or let the cat walk on it.</text>
  <g font-family="{MONO}" font-size="11">
    <rect x="134" y="146" width="92" height="22" rx="11" fill="{C["bar"]}" stroke="{C["border"]}"/>
    <text x="180" y="161" fill="{C["mint"]}" text-anchor="middle">● free</text>
    <rect x="234" y="146" width="96" height="22" rx="11" fill="{C["bar"]}" stroke="{C["border"]}"/>
    <text x="282" y="161" fill="{C["text"]}" text-anchor="middle">macOS</text>
    <rect x="338" y="146" width="96" height="22" rx="11" fill="{C["bar"]}" stroke="{C["border"]}"/>
    <text x="386" y="161" fill="{C["text"]}" text-anchor="middle">Windows</text>
  </g>
  <g>
    {keys_s}
  </g>
  {paw}
  {lock}
'''
    return svg(H, "Now shipping: Paws Off — pause your keyboard with one click", body)


# ---------------------------------------------------------------- process
def process():
    H = 290
    T = "9s"  # one loop; stages at 0–⅓, ⅓–⅔, ⅔–1

    def stage_vals(i):
        # 1 while stage i is active, else 0
        a, b = i / 3, (i + 1) / 3
        if i == 0:
            return "1;1;0;0", f"0;{b-0.01:.3f};{b:.3f};1"
        if i == 2:
            return "0;0;1;1", f"0;{a-0.01:.3f};{a:.3f};1"
        return "0;0;1;1;0;0", f"0;{a-0.01:.3f};{a:.3f};{b-0.01:.3f};{b:.3f};1"

    steps = [("01", "sketch", "rough it out, fast"),
             ("02", "design", "make it feel right"),
             ("03", "ship", "get it into hands")]
    left = []
    for i, (num, name, cap) in enumerate(steps):
        y = 92 + i * 62
        v, kt = stage_vals(i)
        left.append(f'''<g>
      <text x="32" y="{y}" fill="{C["dim"]}" font-family="{MONO}" font-size="12">{num}</text>
      <text x="62" y="{y}" fill="{C["dim"]}" font-family="{SANS}" font-size="20" font-weight="700">{name}</text>
      <text x="62" y="{y}" fill="{C["text"]}" font-family="{SANS}" font-size="20" font-weight="700" opacity="0">{name}<animate attributeName="opacity" values="{v}" keyTimes="{kt}" dur="{T}" repeatCount="indefinite"/></text>
      <text x="62" y="{y+20}" fill="{C["muted"]}" font-family="{MONO}" font-size="12" opacity="0">{cap}<animate attributeName="opacity" values="{v}" keyTimes="{kt}" dur="{T}" repeatCount="indefinite"/></text>
      <rect x="22" y="{y-17}" width="3" height="42" rx="1.5" fill="{C["amber"]}" opacity="0"><animate attributeName="opacity" values="{v}" keyTimes="{kt}" dur="{T}" repeatCount="indefinite"/></rect>
    </g>''')
    left_s = "\n    ".join(left)

    # the card being made, centred in the canvas
    cx, cy, cw, ch = 421, 72, 300, 168

    sk = C["muted"]
    fill_in = f'<animate attributeName="fill-opacity" values="0;0;1;1" keyTimes="0;0.34;0.45;1" dur="{T}" repeatCount="indefinite"/>'
    stroke_fade = f'<animate attributeName="stroke-opacity" values="1;1;0;0" keyTimes="0;0.34;0.45;1" dur="{T}" repeatCount="indefinite"/>'

    def part(tag, attrs, length, fill):
        return (f'<{tag} {attrs} fill="{fill}" fill-opacity="0" stroke="{sk}" stroke-width="1.5" '
                f'stroke-dasharray="{length}" stroke-dashoffset="{length}">'
                f'<animate attributeName="stroke-dashoffset" values="{length};{length};0;0" keyTimes="0;0.03;0.26;1" dur="{T}" repeatCount="indefinite"/>'
                f'{fill_in}{stroke_fade}</{tag}>')

    card = "\n      ".join([
        part("rect", f'x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16"', 2 * (cw + ch), C["bar"]),
        part("circle", f'cx="{cx+38}" cy="{cy+40}" r="18"', 114, C["violet"]),
        part("rect", f'x="{cx+68}" y="{cy+28}" width="140" height="11" rx="5.5"', 302, C["text"]),
        part("rect", f'x="{cx+68}" y="{cy+46}" width="190" height="8" rx="4"', 396, C["dim"]),
        part("rect", f'x="{cx+20}" y="{cy+76}" width="{cw-40}" height="8" rx="4"', 2 * (cw - 40) + 16, C["grid"]),
        part("rect", f'x="{cx+20}" y="{cy+92}" width="{cw-110}" height="8" rx="4"', 2 * (cw - 110) + 16, C["grid"]),
        part("rect", f'x="{cx+20}" y="{cy+118}" width="{cw-40}" height="34" rx="10"', 2 * (cw - 40 + 34), C["violet"]),
    ])

    # stage-2 extras: lock glyph + button label appear with the colour
    reveal = f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.36;0.46;1" dur="{T}" repeatCount="indefinite"/>'
    details = f'''<g opacity="0">{reveal}
        <rect x="{cx+31}" y="{cy+39}" width="14" height="10" rx="2" fill="{C["bg"]}"/>
        <path d="M{cx+34} {cy+39}v-3a4 4 0 0 1 8 0v3" stroke="{C["bg"]}" stroke-width="2" fill="none"/>
        <text x="{cx+cw/2}" y="{cy+140}" fill="{C["bg"]}" font-family="{SANS}" font-size="13" font-weight="700" text-anchor="middle">Lock keyboard</text>
      </g>'''

    # sketch-stage annotations (redlines) that disappear when designed
    hide = f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.1;0.16;0.32;0.36;1" dur="{T}" repeatCount="indefinite"/>'
    redlines = f'''<g opacity="0" font-family="{MONO}" font-size="10" fill="#ff7a7a">{hide}
        <line x1="{cx}" y1="{cy-12}" x2="{cx+cw}" y2="{cy-12}" stroke="#ff7a7a" stroke-width="1"/>
        <line x1="{cx}" y1="{cy-16}" x2="{cx}" y2="{cy-8}" stroke="#ff7a7a"/><line x1="{cx+cw}" y1="{cy-16}" x2="{cx+cw}" y2="{cy-8}" stroke="#ff7a7a"/>
        <text x="{cx+cw/2}" y="{cy-16}" text-anchor="middle">{cw}</text>
        <text x="{cx+cw+10}" y="{cy+139}">← 1 job, 1 tap</text>
      </g>'''

    # stage 3: card lifts, stamp lands, progress bar fills
    lift = f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -8;0 -8;0 0" keyTimes="0;0.67;0.72;0.98;1" dur="{T}" repeatCount="indefinite"/>'
    stamp = f'''<g transform="translate({cx+cw-28} {cy+18}) rotate(-12)">
      <g opacity="0">
        <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.74;0.76;0.98;1" dur="{T}" repeatCount="indefinite"/>
        <animateTransform attributeName="transform" type="scale" values="2.2;2.2;1;1" keyTimes="0;0.74;0.78;1" dur="{T}" repeatCount="indefinite"/>
        <rect x="-50" y="-15" width="100" height="30" rx="6" fill="{C["bg"]}" stroke="{C["mint"]}" stroke-width="2"/>
        <text y="5" fill="{C["mint"]}" font-family="{MONO}" font-size="13" font-weight="700" text-anchor="middle">✓ SHIPPED</text>
      </g>
    </g>'''
    bar_w = cw
    progress = f'''<g opacity="0">
      <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.67;0.68;0.98;1" dur="{T}" repeatCount="indefinite"/>
      <rect x="{cx}" y="{cy+ch+18}" width="{bar_w}" height="4" rx="2" fill="{C["grid"]}"/>
      <rect x="{cx}" y="{cy+ch+18}" width="0" height="4" rx="2" fill="{C["mint"]}">
        <animate attributeName="width" values="0;0;{bar_w};{bar_w}" keyTimes="0;0.68;0.8;1" dur="{T}" repeatCount="indefinite"/>
      </rect>
      <text x="{cx}" y="{cy+ch+38}" fill="{C["muted"]}" font-family="{MONO}" font-size="11">git push · notarize · release</text>
      <text x="{cx+cw}" y="{cy+ch+38}" fill="{C["mint"]}" font-family="{MONO}" font-size="11" text-anchor="end" opacity="0">live<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.79;0.8;1" dur="{T}" repeatCount="indefinite"/></text>
    </g>'''

    body = f'''{window(H, "process — how a thing gets made", "loop ∞")}
  <rect x="300" y="39" width="{W-301}" height="{H-40}" fill="url(#dots)"/>
  <line x1="300" y1="38" x2="300" y2="{H-1}" stroke="{C["border"]}"/>
  {left_s}
  <g>{lift}
      {card}
      {details}
      {redlines}
    {stamp}
  </g>
  {progress}'''
    return svg(H, "Process: sketch, design, ship", body)


# ---------------------------------------------------------------- toolkit
def toolkit():
    H = 372
    groups = [
        ("Design", C["violet"], ["Figma", "Design Systems", "Prototyping", "UX Research", "B2B & Internal Tools"]),
        ("Build", C["mint"], ["Swift · SwiftUI", "AppKit", "C# · WPF", "JavaScript", "Vue"]),
        ("AI", C["amber"], ["Claude Code", "Spec-driven builds", "Ship first", "Polish second"]),
    ]
    LP = 196          # layers panel width
    fx0, fy, fw, fh, fg = LP + 26, 88, 192, 230, 16

    # layers panel
    layers = [f'<rect x="1" y="39" width="{LP-1}" height="{H-40}" fill="{C["panel"]}"/>',
              f'<line x1="{LP}" y1="38" x2="{LP}" y2="{H-1}" stroke="{C["border"]}"/>',
              f'<text x="18" y="64" fill="{C["muted"]}" font-family="{SANS}" font-size="11" font-weight="700" letter-spacing="1">LAYERS</text>']
    ly = 92
    sel_rows = []
    for gi, (name, col, items) in enumerate(groups):
        # highlight row tracks the cursor
        sel_rows.append(ly)
        layers.append(f'<text x="18" y="{ly}" fill="{C["dim"]}" font-family="{SANS}" font-size="11">▾</text>'
                      f'<text x="34" y="{ly}" fill="{col}" font-family="{MONO}" font-size="12">#</text>'
                      f'<text x="50" y="{ly}" fill="{C["text"]}" font-family="{SANS}" font-size="13" font-weight="600">{name}</text>'
                      f'<text x="{LP-16}" y="{ly}" fill="{C["dim"]}" font-family="{MONO}" font-size="11" text-anchor="end">{len(items)}</text>')
        ly += 22
        for it in items[:2]:
            layers.append(f'<text x="50" y="{ly}" fill="{C["dim"]}" font-family="{MONO}" font-size="11">◇</text>'
                          f'<text x="66" y="{ly}" fill="{C["muted"]}" font-family="{SANS}" font-size="12">{esc(it)}</text>')
            ly += 20
        layers.append(f'<text x="66" y="{ly}" fill="{C["dim"]}" font-family="{SANS}" font-size="12">+{len(items)-2} more</text>')
        ly += 34

    # frames
    frames = []
    for gi, (name, col, items) in enumerate(groups):
        x = fx0 + gi * (fw + fg)
        frames.append(f'<text x="{x}" y="{fy-10}" fill="{C["muted"]}" font-family="{SANS}" font-size="12">#  {name}</text>')
        frames.append(f'<rect x="{x}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="{C["bar"]}" stroke="{C["border"]}"/>')
        frames.append(f'<rect x="{x}" y="{fy}" width="{fw}" height="4" rx="2" fill="{col}"/>')
        for i, it in enumerate(items):
            cy = fy + 24 + i * 40
            frames.append(f'<rect x="{x+14}" y="{cy}" width="{fw-28}" height="30" rx="8" fill="{C["bg"]}" stroke="{C["border"]}"/>'
                          f'<circle cx="{x+30}" cy="{cy+15}" r="4" fill="{col}"/>'
                          f'<text x="{x+44}" y="{cy+19.5}" fill="{C["text"]}" font-family="{SANS}" font-size="13">{esc(it)}</text>')

    # selection box + layer highlight + multiplayer cursor, all on one 9s loop
    T = "9s"
    xs = [fx0 + i * (fw + fg) for i in range(3)]
    kt = "0;0.30;0.333;0.63;0.666;0.96;1"
    sel_x = f"{xs[0]};{xs[0]};{xs[1]};{xs[1]};{xs[2]};{xs[2]};{xs[0]}"
    selection = f'''<g>
    <animateTransform attributeName="transform" type="translate" values="{";".join(f"{int(v)-xs[0]} 0" for v in sel_x.split(";"))}" keyTimes="{kt}" dur="{T}" repeatCount="indefinite" calcMode="spline" keySplines="{";".join(["0.6 0 0.2 1"]*6)}"/>
    <rect x="{xs[0]-1}" y="{fy-1}" width="{fw+2}" height="{fh+2}" rx="11" fill="none" stroke="{C["select"]}" stroke-width="1.5"/>
    {"".join(f'<rect x="{px-3.5}" y="{py-3.5}" width="7" height="7" fill="{C["bg"]}" stroke="{C["select"]}" stroke-width="1.5"/>' for px, py in [(xs[0], fy), (xs[0]+fw, fy), (xs[0], fy+fh), (xs[0]+fw, fy+fh)])}
    <rect x="{xs[0]+fw/2-34}" y="{fy+fh+8}" width="68" height="18" rx="4" fill="{C["select"]}"/>
    <text x="{xs[0]+fw/2}" y="{fy+fh+21}" fill="#fff" font-family="{SANS}" font-size="11" text-anchor="middle">{fw} × {fh}</text>
  </g>'''
    rows = sel_rows
    row_y = f"{rows[0]};{rows[0]};{rows[1]};{rows[1]};{rows[2]};{rows[2]};{rows[0]}"
    highlight = f'''<rect x="8" y="{rows[0]-15}" width="{LP-16}" height="22" rx="5" fill="{C["select"]}" fill-opacity="0.18">
    <animate attributeName="y" values="{";".join(str(int(v)-15) for v in row_y.split(";"))}" keyTimes="{kt}" dur="{T}" repeatCount="indefinite" calcMode="discrete"/>
  </rect>'''
    # cursor wanders inside each frame, then hops to the next
    pts = []
    for i, x in enumerate(xs):
        pts += [(x + 120, fy + 60), (x + 70, fy + 150)]
    cur_vals = ";".join(f"{x} {y}" for x, y in pts + [pts[0]])
    cur_kt = "0;0.15;0.333;0.48;0.666;0.81;1"
    cursor = f'''<g>
    <animateTransform attributeName="transform" type="translate" values="{cur_vals}" keyTimes="{cur_kt}" dur="{T}" repeatCount="indefinite" calcMode="spline" keySplines="{";".join(["0.5 0 0.3 1"]*6)}"/>
    <path d="M0 0 L0 17 L4.5 12.8 L7.6 19.6 L10.4 18.4 L7.4 11.8 L13 11.6 Z" fill="{C["amber"]}" stroke="{C["bg"]}" stroke-width="1.2" stroke-linejoin="round"/>
    <rect x="12" y="18" width="38" height="19" rx="6" fill="{C["amber"]}"/>
    <text x="31" y="31.5" fill="{C["bg"]}" font-family="{SANS}" font-size="11" font-weight="700" text-anchor="middle">Zee</text>
  </g>'''

    platforms = f'''<text x="{fx0}" y="{H-18}" font-family="{MONO}" font-size="12"><tspan fill="{C["dim"]}">ships to  </tspan><tspan fill="{C["text"]}">macOS  ·  Windows  ·  iOS  ·  Web</tspan></text>
  <text x="{W-20}" y="{H-18}" fill="{C["dim"]}" font-family="{MONO}" font-size="11" text-anchor="end">100%</text>'''

    body = f'''{window(H, "toolkit.fig", "1 collaborator online")}
  <rect x="{LP}" y="39" width="{W-LP-1}" height="{H-40}" fill="url(#dots)"/>
  {"".join(layers)}
  {highlight}
  {"".join(frames)}
  {selection}
  {platforms}
  {cursor}'''
    return svg(H, "Toolkit — Design: Figma, Design Systems, Prototyping, UX Research, B2B & Internal Tools. "
                  "Build: Swift/SwiftUI, AppKit, C#/WPF, JavaScript, Vue. AI: Claude Code, spec-driven builds.", body)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    icon = sys.argv[1] if len(sys.argv) > 1 else None
    for name, s in [("now-shipping.svg", now_shipping(icon)), ("process.svg", process_card.build(C, W, MONO, SANS, window, svg, esc)), ("toolkit.svg", toolkit())]:
        (ASSETS / name).write_text(s)
        print(f"wrote {name} ({len(s)//1024} KB)")
