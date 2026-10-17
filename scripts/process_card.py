"""process.svg — observe → sketch → design → build → ship, looping back.

Product-agnostic on purpose: no app names or app-specific icons.
Timeline: one 15s loop, five 3s stages. Every animation is written as a list
of (time_fraction, value) points so the choreography reads top to bottom.
"""
import math

T = 15  # seconds per loop


def anim(attr, pts, extra=""):
    pts = sorted(pts)
    if pts[0][0] != 0:
        pts = [(0, pts[0][1])] + pts
    if pts[-1][0] != 1:
        pts = pts + [(1, pts[-1][1])]
    vals = ";".join(str(v) for _, v in pts)
    kt = ";".join(f"{t:.4f}" for t, _ in pts)
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"{extra}/>'


def anim_t(kind, pts, spline=True):
    pts = sorted(pts)
    if pts[0][0] != 0:
        pts = [(0, pts[0][1])] + pts
    if pts[-1][0] != 1:
        pts = pts + [(1, pts[-1][1])]
    vals = ";".join(str(v) for _, v in pts)
    kt = ";".join(f"{t:.4f}" for t, _ in pts)
    sp = ""
    if spline:
        sp = f' calcMode="spline" keySplines="{";".join(["0.5 0 0.3 1"] * (len(pts) - 1))}"'
    return (f'<animateTransform attributeName="transform" type="{kind}" values="{vals}" '
            f'keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"{sp}/>')


def visible(a, b, f=0.012):
    """opacity 1 between a and b, 0 elsewhere"""
    pts = [(0, 1)] if a <= 0 else [(0, 0), (a, 0), (min(a + f, 1), 1)]
    pts += [(1, 1)] if b >= 1 else [(b - f, 1), (b, 0), (1, 0)]
    return anim("opacity", pts)


def build(C, W, MONO, SANS, window, svg, esc):
    H = 340
    LP = 300                       # left panel width
    S = [i / 5 for i in range(6)]  # stage boundaries 0, .2, .4, .6, .8, 1

    # ------------------------------------------------------------ left list
    steps = [("01", "observe", "find the real problem"),
             ("02", "sketch", "rough it out, fast"),
             ("03", "design", "make it feel right"),
             ("04", "build", "code it, test it"),
             ("05", "ship", "get it into hands")]
    left = []
    for i, (num, name, cap) in enumerate(steps):
        y = 84 + i * 52
        on = visible(S[i], S[i + 1])
        left.append(f'''<g>
      <text x="32" y="{y}" fill="{C["dim"]}" font-family="{MONO}" font-size="12">{num}</text>
      <text x="62" y="{y}" fill="{C["dim"]}" font-family="{SANS}" font-size="19" font-weight="700">{name}</text>
      <g opacity="0">{on}
        <text x="62" y="{y}" fill="{C["text"]}" font-family="{SANS}" font-size="19" font-weight="700">{name}</text>
        <text x="62" y="{y+18}" fill="{C["muted"]}" font-family="{MONO}" font-size="11">{cap}</text>
        <rect x="22" y="{y-16}" width="3" height="40" rx="1.5" fill="{C["amber"]}"/>
      </g>
    </g>''')
    # a faint loop arrow from ship back up to observe
    left.append(f'''<path d="M268 296 C 290 296, 290 78, 268 78" stroke="{C["border"]}" stroke-width="1.2" stroke-dasharray="3 4" fill="none"/>
    <path d="M272 73 L264 78 L272 83" stroke="{C["border"]}" stroke-width="1.2" fill="none"/>''')
    left_s = "\n    ".join(left)

    # ------------------------------------------------------------ 01 observe
    notes = [((380, 86), "too slow", -4), ((488, 74), "lost my work", 3), ((690, 82), "where's undo?", -3),
             ((786, 128), "?!", 5), ((364, 176), "confusing", 3), ((760, 206), "could it also…?", -4),
             ((424, 270), "bug #12", -2), ((664, 276), "love this", 4)]
    chosen = (571, 178)
    NW, NH = 92, 46

    def note(cx, cy, label, rot, fill, stroke, tcol):
        return (f'<g transform="translate({cx} {cy}) rotate({rot})">'
                f'<rect x="{-NW/2}" y="{-NH/2}" width="{NW}" height="{NH}" rx="5" fill="{fill}" stroke="{stroke}"/>'
                f'<line x1="{-NW/2+10}" y1="{NH/2-12}" x2="{NW/2-26}" y2="{NH/2-12}" stroke="{C["grid"]}" stroke-width="3" stroke-linecap="round"/>'
                f'<text x="{-NW/2+10}" y="-3" fill="{tcol}" font-family="{MONO}" font-size="10.5">{esc(label)}</text></g>')

    dim_others = anim("opacity", [(0, 1), (0.145, 1), (0.16, 0.28)])
    others = "".join(note(x, y, l, r, C["bar"], C["border"], C["muted"]) for (x, y), l, r in notes)
    chosen_plain = note(*chosen, "why 3 taps?", -1, C["bar"], C["border"], C["muted"])
    chosen_lit = note(*chosen, "why 3 taps?", -1, "#2a2414", C["amber"], C["amber"])

    # viewfinder: corner brackets + a small rotating iris; wanders, then locks on
    bw, bh = 128, 82

    def corners(w, h, L=14):
        x0, y0, x1, y1 = -w/2, -h/2, w/2, h/2
        return (f"M{x0} {y0+L}V{y0}H{x0+L} M{x1-L} {y0}H{x1}V{y0+L} "
                f"M{x1} {y1-L}V{y1}H{x1-L} M{x0+L} {y1}H{x0}V{y1-L}")

    blades = []
    R = 9
    for i in range(8):
        a0 = math.radians(i * 45)
        p1 = (R * math.cos(a0), R * math.sin(a0))
        a1 = a0 + math.radians(80)
        p2 = (R * math.cos(a1), R * math.sin(a1))
        p3 = (R * .3 * math.cos(a0 + math.radians(112)), R * .3 * math.sin(a0 + math.radians(112)))
        blades.append(f'M{p1[0]:.2f},{p1[1]:.2f} A{R},{R} 0 0 1 {p2[0]:.2f},{p2[1]:.2f} L{p3[0]:.2f},{p3[1]:.2f}Z')
    iris = (f'<g transform="translate({bw/2-4} {-bh/2-2})"><circle r="11.5" fill="{C["bg"]}" stroke="{C["amber"]}" stroke-width="1.2"/>'
            f'<g>{anim_t("rotate", [(0, 0), (1, 360)], spline=False)}'
            f'<path d="{" ".join(blades)}" fill="{C["violet"]}" stroke="{C["bg"]}" stroke-width="0.8"/></g></g>')
    path_pts = [(0.01, "430 120"), (0.05, "660 118"), (0.09, "470 236"), (0.13, f"{chosen[0]} {chosen[1]}")]
    finder = f'''<g>
      {anim_t("translate", path_pts)}
      <g>
        {anim_t("scale", [(0, 1.15), (0.13, 1.15), (0.15, 1)])}
        <path d="{corners(bw, bh)}" stroke="{C["muted"]}" stroke-width="2" fill="none" stroke-linecap="round">
          {anim("stroke", [(0, C["muted"]), (0.13, C["muted"]), (0.145, C["amber"])])}
        </path>
        {iris}
      </g>
    </g>'''
    tag = f'''<g opacity="0">{visible(0.15, S[1])}
      <rect x="{chosen[0]-62}" y="{chosen[1]+50}" width="124" height="22" rx="11" fill="{C["amber"]}"/>
      <text x="{chosen[0]}" y="{chosen[1]+65}" fill="{C["bg"]}" font-family="{MONO}" font-size="11" font-weight="700" text-anchor="middle">the real problem</text>
    </g>'''
    observe = f'''<g opacity="0">{visible(0, S[1])}
      <g>{dim_others}{others}</g>
      {chosen_plain}
      <g opacity="0">{visible(0.145, S[1])}{chosen_lit}</g>
      {finder}
      {tag}
    </g>'''

    # ------------------------------------------------------------ 02–05 the card
    cx, cy, cw, ch = 421, 98, 300, 168
    ccx, ccy = cx + cw / 2, cy + ch / 2
    sk = C["muted"]
    draw_a, draw_b = S[1] + 0.01, S[1] + 0.12      # sketch strokes draw in
    fill_a, fill_b = S[2], S[2] + 0.05             # design: colour arrives
    fill_in = anim("fill-opacity", [(0, 0), (fill_a, 0), (fill_b, 1)])
    stroke_out = anim("stroke-opacity", [(0, 1), (fill_a, 1), (fill_b, 0)])

    def part(tag, attrs, length, fill):
        return (f'<{tag} {attrs} fill="{fill}" fill-opacity="0" stroke="{sk}" stroke-width="1.5" '
                f'stroke-dasharray="{length}" stroke-dashoffset="{length}">'
                f'{anim("stroke-dashoffset", [(0, length), (draw_a, length), (draw_b, 0)])}'
                f'{fill_in}{stroke_out}</{tag}>')

    face = "\n        ".join([
        part("rect", f'x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16"', 2 * (cw + ch), C["bar"]),
        part("rect", f'x="{cx+20}" y="{cy+22}" width="36" height="36" rx="10"', 144, C["violet"]),
        part("rect", f'x="{cx+70}" y="{cy+26}" width="140" height="11" rx="5.5"', 302, C["text"]),
        part("rect", f'x="{cx+70}" y="{cy+44}" width="190" height="8" rx="4"', 396, C["dim"]),
        part("rect", f'x="{cx+20}" y="{cy+76}" width="{cw-40}" height="8" rx="4"', 2 * (cw - 40) + 16, C["grid"]),
        part("rect", f'x="{cx+20}" y="{cy+92}" width="{cw-110}" height="8" rx="4"', 2 * (cw - 110) + 16, C["grid"]),
        part("rect", f'x="{cx+20}" y="{cy+118}" width="{cw-40}" height="34" rx="10"', 2 * (cw - 40 + 34), C["violet"]),
    ])
    details = f'''<g opacity="0">{anim("opacity", [(0, 0), (fill_a + 0.02, 0), (fill_b + 0.01, 1)])}
        <circle cx="{cx+38}" cy="{cy+40}" r="7" fill="#fff"/>
        <text x="{ccx}" y="{cy+140}" fill="{C["bg"]}" font-family="{SANS}" font-size="13" font-weight="700" text-anchor="middle">Continue</text>
      </g>'''
    redlines = f'''<g opacity="0" font-family="{MONO}" font-size="10" fill="#ff7a7a">{visible(S[1] + 0.06, S[2] + 0.01)}
        <line x1="{cx}" y1="{cy-12}" x2="{cx+cw}" y2="{cy-12}" stroke="#ff7a7a"/>
        <line x1="{cx}" y1="{cy-16}" x2="{cx}" y2="{cy-8}" stroke="#ff7a7a"/><line x1="{cx+cw}" y1="{cy-16}" x2="{cx+cw}" y2="{cy-8}" stroke="#ff7a7a"/>
        <text x="{ccx}" y="{cy-16}" text-anchor="middle">{cw}</text>
        <text x="{cx+cw+8}" y="{cy+139}">← one clear</text>
        <text x="{cx+cw+20}" y="{cy+153}">action</text>
      </g>'''

    # flip: face → code (build) → face (ship)
    f0, f1 = S[3], S[3] + 0.02          # flip to code
    b0, b1 = S[4] - 0.02, S[4]          # flip back
    face_flip = anim_t("scale", [(0, "1 1"), (f0, "1 1"), (f1, "0.001 1"), (b0, "0.001 1"), (b1, "1 1")])
    code_flip = anim_t("scale", [(0, "0.001 1"), (f1, "0.001 1"), (f1 + 0.02, "1 1"), (b0 - 0.005, "1 1"), (b0 + 0.005, "0.001 1")])

    code_lines = [
        [("struct ", C["violet"]), ("Card", C["amber"]), (": View {", C["text"])],
        [("  var ", C["violet"]), ("body: some View {", C["text"])],
        [("    Button(", C["text"]), ('"Continue"', C["mint"]), (") {", C["text"])],
        [("      next()", C["text"])],
        [("    }", C["text"])],
        [("  }", C["text"])],
        [("}", C["text"])],
    ]
    code = []
    for k, segs in enumerate(code_lines):
        y = cy + 46 + k * 15
        t_on = f1 + 0.02 + k * 0.012
        indent = len(segs[0][0]) - len(segs[0][0].lstrip(" "))
        segs = [(segs[0][0].lstrip(" "), segs[0][1])] + segs[1:]
        spans = "".join(f'<tspan fill="{col}">{esc(s)}</tspan>' for s, col in segs)
        code.append(f'<g opacity="0">{anim("opacity", [(0, 0), (t_on, 0), (t_on + 0.004, 1)])}'
                    f'<text x="{cx+16}" y="{y}" fill="{C["dim"]}" font-family="{MONO}" font-size="11">{k+1}</text>'
                    f'<text x="{cx+36+indent*7:.1f}" y="{y}" font-family="{MONO}" font-size="11.5">{spans}</text></g>')
    t_test = f1 + 0.02 + 7 * 0.012 + 0.02
    code_panel = f'''<g opacity="0">{anim("opacity", [(0, 0), (f1, 0), (f1 + 0.001, 1), (b0 + 0.004, 1), (b0 + 0.005, 0)])}
        <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="16" fill="#0a0810" stroke="{C["border"]}"/>
        <line x1="{cx}" y1="{cy+28}" x2="{cx+cw}" y2="{cy+28}" stroke="{C["border"]}"/>
        <text x="{cx+16}" y="{cy+19}" fill="{C["muted"]}" font-family="{MONO}" font-size="11">Card.swift</text>
        {"".join(code)}
        <g opacity="0">{anim("opacity", [(0, 0), (t_test, 0), (t_test + 0.006, 1)])}
          <rect x="{cx+16}" y="{cy+ch-24}" width="{cw-32}" height="1" fill="{C["border"]}"/>
          <text x="{cx+16}" y="{cy+ch-9}" fill="{C["mint"]}" font-family="{MONO}" font-size="11">✓ 24 tests passed</text>
        </g>
      </g>'''

    # ship: lift, stamp, release bar, then feedback bubble that flies back to "observe"
    lift = anim_t("translate", [(0, "0 0"), (S[4], "0 0"), (S[4] + 0.02, "0 -8"), (0.985, "0 -8"), (1, "0 0")])
    stamp = f'''<g transform="translate({cx+cw-30} {cy+16}) rotate(-12)">
      <g opacity="0">{visible(S[4] + 0.03, 1)}
        {anim_t("scale", [(0, 2.2), (S[4] + 0.03, 2.2), (S[4] + 0.05, 1)], spline=False)}
        <rect x="-50" y="-15" width="100" height="30" rx="6" fill="{C["bg"]}" stroke="{C["mint"]}" stroke-width="2"/>
        <text y="5" fill="{C["mint"]}" font-family="{MONO}" font-size="13" font-weight="700" text-anchor="middle">✓ SHIPPED</text>
      </g>
    </g>'''
    progress = f'''<g opacity="0">{visible(S[4], 1)}
      <rect x="{cx}" y="{cy+ch+20}" width="{cw}" height="4" rx="2" fill="{C["grid"]}"/>
      <rect x="{cx}" y="{cy+ch+20}" width="0" height="4" rx="2" fill="{C["mint"]}">{anim("width", [(0, 0), (S[4], 0), (S[4] + 0.06, cw)])}</rect>
      <text x="{cx}" y="{cy+ch+40}" fill="{C["muted"]}" font-family="{MONO}" font-size="11">build · sign · release</text>
      <text x="{cx+cw}" y="{cy+ch+40}" fill="{C["mint"]}" font-family="{MONO}" font-size="11" text-anchor="end" opacity="0">live{anim("opacity", [(0, 0), (S[4] + 0.06, 0), (S[4] + 0.065, 1)])}</text>
    </g>'''
    bx, by = 318, cy - 40
    bubble = f'''<g opacity="0">{anim("opacity", [(0, 0), (0.885, 0), (0.9, 1), (0.955, 1), (0.99, 0)])}
      {anim_t("translate", [(0, "0 0"), (0.955, "0 0"), (0.99, "-40 -150")])}
      <path d="M{bx} {by+12}a12 12 0 0 1 12-12h168a12 12 0 0 1 12 12v12a12 12 0 0 1-12 12h-150l-14 10 2-10h-6a12 12 0 0 1-12-12z" fill="{C["text"]}"/>
      <circle cx="{bx+16}" cy="{by+18}" r="7" fill="{C["violet"]}"/>
      <text x="{bx+30}" y="{by+22}" fill="{C["bg"]}" font-family="{SANS}" font-size="12.5" font-weight="600">love it — could it also…?</text>
    </g>'''

    card = f'''<g opacity="0">{anim("opacity", [(0, 0), (S[1], 0), (S[1] + 0.001, 1), (0.985, 1), (1, 0)])}
    <g>{lift}
      <g transform="translate({ccx} {ccy})"><g>{face_flip}<g transform="translate({-ccx} {-ccy})">
        {face}
        {details}
      </g></g></g>
      <g transform="translate({ccx} {ccy})"><g>{code_flip}<g transform="translate({-ccx} {-ccy})">
      {code_panel}
      </g></g></g>
      {redlines}
      {stamp}
    </g>
    {progress}
  </g>'''

    body = f'''{window(H, "process — how a thing gets made", "loop ∞")}
  <rect x="{LP}" y="39" width="{W-LP-1}" height="{H-40}" fill="url(#dots)"/>
  <line x1="{LP}" y1="38" x2="{LP}" y2="{H-1}" stroke="{C["border"]}"/>
  {left_s}
  {observe}
  {card}
  {bubble}'''
    return svg(H, "Process: observe, sketch, design, build, ship — then loop back on feedback", body)
