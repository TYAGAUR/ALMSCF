"""Tiny SVG diagram toolkit: boxes, arrows, flowcharts, sequence diagrams."""
from html import escape

NAVY = "#1B2559"; INDIGO = "#4F5BD5"; TEAL = "#17A2A0"; AMBER = "#F2A33A"; ROSE = "#E5484D"
GREEN = "#2E9E6B"; INK = "#1F2433"; MUTED = "#6B7390"; LINE = "#B9C0DA"; PALE = "#EEF1FB"
PALE_T = "#E3F6F5"; PALE_A = "#FDF1DC"; PALE_R = "#FCE7E8"; PALE_G = "#E2F4EA"; WHITE = "#FFFFFF"
VIOLET = "#7C5CD6"; PALE_V = "#EFEAFB"

KIND = {  # fill, stroke, text
    "std": (WHITE, INDIGO, INK), "ui": (PALE, INDIGO, NAVY), "api": (PALE_T, TEAL, "#0B5F5D"),
    "db": (PALE_A, AMBER, "#7A4B05"), "ext": (PALE_V, VIOLET, "#3D2A8A"), "ok": (PALE_G, GREEN, "#17613F"),
    "bad": (PALE_R, ROSE, "#8A1F24"), "dark": (NAVY, NAVY, WHITE), "grey": ("#F4F5F9", LINE, MUTED),
    "warn": (PALE_A, AMBER, "#7A4B05"),
}


class S:
    def __init__(s, w, h):
        s.w, s.h, s.p, s.colors = w, h, [], set()

    def _a(s, color):
        s.colors.add(color)
        return f'url(#ah{color[1:]})'

    def rect(s, x, y, w, h, fill=WHITE, stroke=LINE, rx=8, sw=1.3, dash=None, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                   f'stroke-width="{sw}"{d} opacity="{op}"/>')

    def text(s, x, y, t, size=13, fill=INK, weight=400, anchor="middle", italic=False, lh=1.25):
        lines = str(t).split("\n")
        y0 = y - (len(lines) - 1) * size * lh / 2
        st = ' font-style="italic"' if italic else ""
        for i, ln in enumerate(lines):
            s.p.append(f'<text x="{x}" y="{y0 + i * size * lh + size * 0.35:.1f}" font-size="{size}" fill="{fill}" '
                       f'font-weight="{weight}" text-anchor="{anchor}"{st}>{escape(ln)}</text>')

    def box(s, x, y, w, h, label, kind="std", size=13, sub=None, rx=8, weight=600, dash=None):
        f, st, tx = KIND[kind]
        s.rect(x, y, w, h, f, st, rx, dash=dash)
        if sub:
            nl = label.count("\n") + 1
            s.text(x + w / 2, y + h / 2 - size * 0.55 * nl + 1, label, size, tx, weight)
            s.text(x + w / 2, y + h / 2 + size * 0.75 * (nl) - 1, sub, size - 2.5, MUTED, 400)
        else:
            s.text(x + w / 2, y + h / 2, label, size, tx, weight)

    def cyl(s, x, y, w, h, label, kind="db", size=13):
        f, st, tx = KIND[kind]
        e = 9
        s.p.append(f'<path d="M{x},{y+e} v{h-2*e} a{w/2},{e} 0 0 0 {w},0 v{-(h-2*e)} a{w/2},{e} 0 0 0 {-w},0 '
                   f'a{w/2},{e} 0 0 0 {w},0" fill="{f}" stroke="{st}" stroke-width="1.3"/>')
        s.text(x + w / 2, y + h / 2 + 4, label, size, tx, 600)

    def diamond(s, x, y, w, h, label, kind="warn", size=12):
        f, st, tx = KIND[kind]
        s.p.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="{f}" '
                   f'stroke="{st}" stroke-width="1.3"/>')
        s.text(x + w / 2, y + h / 2, label, size, tx, 600)

    def pill(s, x, y, w, h, label, fill=INDIGO, color=WHITE, size=12):
        s.rect(x, y, w, h, fill, fill, rx=h / 2, sw=0)
        s.text(x + w / 2, y + h / 2, label, size, color, 700)

    def circle(s, cx, cy, r, label, fill=INDIGO, color=WHITE, size=13):
        s.p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>')
        s.text(cx, cy, label, size, color, 700)

    def line(s, x1, y1, x2, y2, color=LINE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def arrow(s, pts, color=MUTED, dash=None, label=None, lpos=None, size=11.5, sw=1.6, both=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        ms = f' marker-start="{s._a(color)}"' if both else ""
        s.p.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} '
                   f'marker-end="{s._a(color)}"{ms} stroke-linejoin="round"/>')
        if label:
            if lpos is None:
                mid = len(pts) // 2
                a, b = pts[mid - 1], pts[mid]
                lpos = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 8)
            w = len(max(label.split("\n"), key=len)) * size * 0.56 + 8
            nl = label.count("\n") + 1
            s.p.append(f'<rect x="{lpos[0]-w/2:.1f}" y="{lpos[1]-size*0.8*nl/2-2:.1f}" width="{w:.1f}" '
                       f'height="{size*1.25*nl+2:.1f}" fill="white" opacity="0.92" rx="3"/>')
            s.text(lpos[0], lpos[1], label, size, MUTED, 500)

    def svg(s, maxw=None):
        defs = "".join(
            f'<marker id="ah{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in s.colors)
        st = f' style="max-width:{maxw}px"' if maxw else ""
        return (f'<svg class="dg" viewBox="0 0 {s.w} {s.h}" xmlns="http://www.w3.org/2000/svg"{st} '
                f'font-family="Segoe UI, Arial, sans-serif"><defs>{defs}</defs>{"".join(s.p)}</svg>')


class Flow(S):
    """Flowchart with named nodes and auto-routed connectors."""

    def __init__(s, w, h):
        super().__init__(w, h)
        s.n = {}

    def node(s, id, x, y, w, h, label, kind="std", shape="box", size=13, sub=None):
        s.n[id] = (x, y, w, h)
        if shape == "box": s.box(x, y, w, h, label, kind, size, sub)
        elif shape == "db": s.cyl(x, y, w, h, label, kind, size)
        elif shape == "dia": s.diamond(x, y, w, h, label, kind, size - 1)
        elif shape == "pill": s.box(x, y, w, h, label, kind, size, sub, rx=h / 2)

    def _c(s, id):
        x, y, w, h = s.n[id]
        return x + w / 2, y + h / 2

    def link(s, a, b, label=None, color=MUTED, dash=None, mode="auto", lpos=None, both=False, off=0):
        ax, ay, aw, ah = s.n[a]; bx, by, bw, bh = s.n[b]
        acx, acy = ax + aw / 2, ay + ah / 2; bcx, bcy = bx + bw / 2, by + bh / 2
        if mode == "auto":
            mode = "h" if (bx > ax + aw - 2 or bx + bw < ax + 2) and abs(bcy - acy) < max(ah, bh) * 1.6 + 1 or \
                (bx > ax + aw - 2 and abs(bcy - acy) < 200 and not (by > ay + ah or by + bh < ay)) else "v"
            if bx > ax + aw - 2 or bx + bw < ax + 2:
                if not (by >= ay + ah - 2 or by + bh <= ay + 2) or abs(bcx - acx) > abs(bcy - acy):
                    mode = "h"
        if mode == "h":
            if bcx >= acx: p1 = (ax + aw, acy + off); p2 = (bx, bcy + off)
            else: p1 = (ax, acy + off); p2 = (bx + bw, bcy + off)
            mx = (p1[0] + p2[0]) / 2
            pts = [p1, p2] if abs(p1[1] - p2[1]) < 1 else [p1, (mx, p1[1]), (mx, p2[1]), p2]
        else:
            if bcy >= acy: p1 = (acx + off, ay + ah); p2 = (bcx + off, by)
            else: p1 = (acx + off, ay); p2 = (bcx + off, by + bh)
            my = (p1[1] + p2[1]) / 2
            pts = [p1, p2] if abs(p1[0] - p2[0]) < 1 else [p1, (p1[0], my), (p2[0], my), p2]
        s.arrow(pts, color, dash, label, lpos, both=both)


def seq(actors, msgs, w=900, title=None, step=44, colors=None, note_w=0):
    """Sequence diagram. actors: [(key,label,kind)]; msgs: (from,to,text[,'dash'|'note'])."""
    n = len(actors)
    top = 70 if not title else 96
    h = top + step * len(msgs) + 30
    d = S(w, h)
    if title:
        d.text(14, 22, title, 15, NAVY, 700, anchor="start")
    cw = (w - 20) / n
    xs = {a[0]: 10 + cw * (i + 0.5) for i, a in enumerate(actors)}
    for k, lab, kind in actors:
        d.box(xs[k] - cw / 2 + 8, top - 52, cw - 16, 38, lab, kind, 12.5)
        d.line(xs[k], top - 14, xs[k], h - 14, LINE, 1.2, "5,4")
    y = top + 8
    for i, m in enumerate(msgs):
        a, b, t = m[0], m[1], m[2]
        flag = m[3] if len(m) > 3 else ""
        col = TEAL if flag != "dash" else MUTED
        if flag == "note":
            x = xs[a]
            d.rect(x - 110, y - 14, 220, 28, PALE_A, AMBER, 6)
            d.text(x, y, t, 11, "#7A4B05", 500)
        elif a == b:
            x = xs[a]
            d.arrow([(x, y - 8), (x + 38, y - 8), (x + 38, y + 10), (x + 2, y + 10)], col)
            d.text(x + 46, y + 1, t, 11.5, INK, 500, anchor="start")
        else:
            x1, x2 = xs[a], xs[b]
            d.arrow([(x1, y), (x2, y)], col, "5,3" if flag == "dash" else None)
            d.text((x1 + x2) / 2, y - 11, t, 11.5, INK, 500)
        y += step
    return d.svg()
