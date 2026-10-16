#!/usr/bin/env python3
"""Generates assets/header.svg — an animated studio window for the profile README.

Left: a terminal that types itself out. Right: the Observant Systems
eight-blade aperture, slowly rotating and "breathing" open and shut.
Edit LINES below and re-run to change the copy.
"""
import math
from pathlib import Path

W, H = 842, 300
MONO = "ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Courier New', monospace"

C = {
    "bg": "#0e0c14",
    "bar": "#16131f",
    "border": "#2c2740",
    "text": "#ece9f5",
    "muted": "#8a84a3",
    "dim": "#4d4766",
    "violet": "#a78bfa",
    "amber": "#f2c14e",
    "mint": "#6ee7b7",
}

# (kind, content, start_seconds)
#   cmd  -> "$ <content>" typed out character by character
#   out  -> rich tspans, fades in at start
LINES = [
    ("cmd", "whoami", 0.4),
    ("out", [("Zee", C["text"], True), ("  // product designer who ships", C["muted"], False)], 1.3),
    ("cmd", "ls ~/studio", 1.9),
    ("out", [("design-systems   b2b-tools   mac-apps   ai-native-builds", C["violet"], False)], 2.9),
    ("cmd", "cat ~/.manifesto", 3.5),
    ("out", [("Design it. Build it. Ship it.", C["text"], False),
             ("  Less excess, more intention.", C["amber"], False)], 4.7),
]

BOLD = ' font-weight="bold"'
CHAR_W = 8.43  # approx advance of a 14px monospace glyph
X0, Y0, STEP = 24, 74, 32


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def terminal():
    out, defs = [], []
    y = Y0
    for i, (kind, content, t) in enumerate(LINES):
        if kind == "cmd":
            text_w = (2 + len(content)) * CHAR_W
            dur = max(0.35, len(content) * 0.06)
            defs.append(
                f'<clipPath id="type{i}"><rect x="{X0}" y="{y-16}" width="0" height="22">'
                f'<animate attributeName="width" begin="{t}s" dur="{dur:.2f}s" '
                f'fill="freeze" calcMode="discrete" values="{";".join(f"{(k/len(content))*text_w + 2*CHAR_W:.1f}" for k in range(len(content)+1))}"/>'
                f"</rect></clipPath>"
            )
            out.append(
                f'<g clip-path="url(#type{i})"><text x="{X0}" y="{y}" font-family="{MONO}" font-size="14">'
                f'<tspan fill="{C["mint"]}" font-weight="bold">$</tspan><tspan fill="{C["text"]}"> {esc(content)}</tspan></text></g>'
            )
            y += STEP - 7
        else:
            spans = "".join(
                f'<tspan fill="{col}"{BOLD if bold else ""}>{esc(s)}</tspan>'
                for s, col, bold in content
            )
            out.append(
                f'<text x="{X0}" y="{y}" font-family="{MONO}" font-size="14" opacity="0">{spans}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{t}s" dur="0.25s" fill="freeze"/></text>'
            )
            y += STEP + 8
    # final prompt + blinking cursor
    t_end = LINES[-1][2] + 0.4
    out.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t_end}s" dur="0.01s" fill="freeze"/>'
        f'<text x="{X0}" y="{y}" fill="{C["mint"]}" font-family="{MONO}" font-size="14" font-weight="bold">$</text>'
        f'<rect x="{X0+14}" y="{y-13}" width="8" height="16" fill="{C["mint"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.501;1" dur="1s" repeatCount="indefinite"/></rect></g>'
    )
    return "\n  ".join(out), "\n    ".join(defs)


def aperture(cx, cy, R=74):
    """Eight overlapping iris blades inside a ring."""
    blades = []
    shades = [C["violet"], "#8b6cf0"]
    for i in range(8):
        a0 = math.radians(i * 45)
        # blade: outer arc from a0 to a0+80deg, then cut back toward the centre
        p1 = (R * math.cos(a0), R * math.sin(a0))
        a1 = a0 + math.radians(80)
        p2 = (R * math.cos(a1), R * math.sin(a1))
        r_in = R * 0.30
        a2 = a0 + math.radians(112)
        p3 = (r_in * math.cos(a2), r_in * math.sin(a2))
        a3 = a0 + math.radians(67)
        p4 = (r_in * math.cos(a3), r_in * math.sin(a3))
        d = (f"M{p1[0]:.2f},{p1[1]:.2f} A{R},{R} 0 0 1 {p2[0]:.2f},{p2[1]:.2f} "
             f"L{p3[0]:.2f},{p3[1]:.2f} L{p4[0]:.2f},{p4[1]:.2f} Z")
        blades.append(f'<path d="{d}" fill="{shades[i % 2]}" stroke="{C["bg"]}" stroke-width="2" stroke-linejoin="round"/>')
    blades_s = "\n        ".join(blades)
    return f'''<g transform="translate({cx} {cy})">
    <circle r="{R+16}" fill="none" stroke="{C["border"]}" stroke-width="1" stroke-dasharray="2 6"/>
    <circle r="{R+4}" fill="{C["bar"]}" stroke="{C["border"]}" stroke-width="1"/>
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="40s" repeatCount="indefinite"/>
      <g>
        <animateTransform attributeName="transform" type="scale" values="1;0.9;1" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
        {blades_s}
      </g>
    </g>
    <circle r="{R*0.2:.1f}" fill="{C["amber"]}">
      <animate attributeName="r" values="{R*0.16:.1f};{R*0.24:.1f};{R*0.16:.1f}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
    </circle>
    <circle r="{R+4}" fill="none" stroke="{C["violet"]}" stroke-opacity="0.35" stroke-width="1.5"/>
    <text y="{R+40}" fill="{C["muted"]}" font-family="{MONO}" font-size="11" text-anchor="middle" letter-spacing="2">OBSERVANT SYSTEMS</text>
  </g>'''


def build():
    term, defs = terminal()
    svg = f'''<svg viewBox="0 0 {W} {H}" xml:space="preserve" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Zee — product designer who ships">
  <defs>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{C["violet"]}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{C["violet"]}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.8" fill="{C["border"]}"/>
    </pattern>
    {defs}
  </defs>

  <!-- window -->
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>
  <rect x="600" y="38" width="{W-601}" height="{H-39}" fill="url(#grid)"/>
  <rect x="600" y="38" width="{W-601}" height="{H-39}" fill="url(#glow)"/>
  <line x1="600" y1="38" x2="600" y2="{H-1}" stroke="{C["border"]}"/>

  <!-- title bar -->
  <path d="M1 13a12 12 0 0 1 12-12h{W-26}a12 12 0 0 1 12 12v25H1z" fill="{C["bar"]}"/>
  <line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{C["border"]}"/>
  <circle cx="24" cy="19.5" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="19.5" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="19.5" r="6" fill="#27c93f"/>
  <text x="{W/2}" y="24" fill="{C["muted"]}" font-family="{MONO}" font-size="12" text-anchor="middle">zee@observant-systems: ~/studio</text>
  <text x="{W-20}" y="24" fill="{C["dim"]}" font-family="{MONO}" font-size="11" text-anchor="end">⌘ made by zee</text>

  <!-- terminal -->
  {term}

  <!-- aperture -->
  {aperture(721, 158)}
</svg>
'''
    out = Path(__file__).resolve().parent.parent / "assets" / "header.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg)
    print(f"wrote {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    build()
