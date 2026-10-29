"""Shared HTML helpers and the print stylesheet."""
import base64, io, pathlib
from html import escape
from PIL import Image

HERE = pathlib.Path(__file__).parent
SHOTS = pathlib.Path(__file__).parents[0] / "shots"

HEADINGS = []   # (level, number, title, id)
_fig = {"n": 0}


def esc(s): return escape(str(s))


def h1(num, title, lead=""):
    hid = f"s{num}".replace(".", "_")
    HEADINGS.append((1, num, title, hid))
    return (f'<section class="part"><div class="part-in"><div class="part-num">PART {num}</div>'
            f'<h1 id="{hid}">{title}</h1><p class="part-lead">{lead}</p></div></section>')


def h2(num, title):
    hid = f"s{num}".replace(".", "_")
    HEADINGS.append((2, num, title, hid))
    return f'<h2 id="{hid}"><span class="sn">{num}</span>{title}</h2>'


def h3(title): return f"<h3>{title}</h3>"


def p(t, cls=""): return f'<p class="{cls}">{t}</p>'


def ul(items, cls=""): return f'<ul class="{cls}">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items): return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def table(head, rows, cls="", widths=None):
    cg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in widths) + "</colgroup>" if widths else ""
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="t {cls}">{cg}<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


def callout(kind, title, text):
    ic = {"info": "i", "warn": "!", "ok": "✓", "key": "★"}[kind]
    return f'<div class="co {kind}"><div class="ci">{ic}</div><div><b>{title}</b><br>{text}</div></div>'


def fig(content, caption, wide=False):
    _fig["n"] += 1
    return (f'<figure class="fig{" wide" if wide else ""}">{content}'
            f'<figcaption><b>Figure {_fig["n"]}.</b> {caption}</figcaption></figure>')


def _b64(name, maxw=1280, q=80):
    path = SHOTS / f"{name}.png"
    im = Image.open(path).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def shot(name, url, caption, crop_h=None):
    """Real browser screenshot in a window frame."""
    style = f' style="max-height:{crop_h}px;object-fit:cover;object-position:top"' if crop_h else ""
    inner = (f'<div class="win"><div class="bar"><i></i><i></i><i></i><span>{esc(url)}</span></div>'
             f'<img src="{_b64(name)}"{style}/></div>')
    return fig(inner, caption)


def shots2(items, caption):
    """Two screenshots side by side."""
    cells = "".join(f'<div class="win"><div class="bar"><i></i><i></i><i></i><span>{esc(u)}</span></div>'
                    f'<img src="{_b64(n, 1000)}"/></div>' for n, u in items)
    return fig(f'<div class="two">{cells}</div>', caption)


def kpi(items):
    return '<div class="kpis">' + "".join(
        f'<div class="kpi"><div class="kv" style="color:{c}">{v}</div><div class="kl">{l}</div></div>' for v, l, c in items) + "</div>"


def steps(items):
    """Numbered step list with a coloured rail."""
    return '<ol class="steps">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


CSS = r"""
@page { size: A4; margin: 17mm 15mm 19mm 15mm;
  @bottom-left { content: "CFA Learning Hub · Platform Technical Guide"; font: 8pt 'Segoe UI', Arial; color: #8A91AD; }
  @bottom-right { content: "Page " counter(page); font: 8pt 'Segoe UI', Arial; color: #8A91AD; }
  @top-right { content: string(chapter); font: 8pt 'Segoe UI', Arial; color: #8A91AD; } }
@page :first { margin: 0; @bottom-left { content: none } @bottom-right { content: none } @top-right { content: none } }
@page part { margin: 0; @bottom-left { content: none } @bottom-right { content: none } @top-right { content: none } }
:root { --navy:#1B2559; --indigo:#4F5BD5; --teal:#17A2A0; --amber:#F2A33A; --rose:#E5484D; --ink:#1F2433; --muted:#6B7390; --line:#DDE2F2; --pale:#EEF1FB; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: var(--ink); font-size: 9.6pt; line-height: 1.5; margin: 0; }
h1,h2,h3,h4 { color: var(--navy); font-weight: 700; margin: 0; }
h2 { font-size: 17pt; margin: 6mm 0 3mm; padding-bottom: 2mm; border-bottom: 2.2px solid var(--indigo); string-set: chapter content(text); break-after: avoid; }
h2 .sn { display:inline-block; background: var(--indigo); color:#fff; font-size: 10pt; padding: 1px 8px; border-radius: 12px; margin-right: 8px; vertical-align: 3px; }
h3 { font-size: 11.5pt; margin: 5mm 0 1.5mm; color: var(--indigo); break-after: avoid; }
h4 { font-size: 10pt; margin: 3mm 0 1mm; }
p { margin: 0 0 2.2mm; }
ul, ol { margin: 0 0 3mm; padding-left: 5mm; } li { margin-bottom: 1mm; }
a { color: var(--indigo); text-decoration: none; }
code, .mono { font-family: Consolas, 'Cascadia Mono', monospace; font-size: 8.4pt; background: #F1F3FA; padding: 0 3px; border-radius: 3px; color: #2B3470; }
small, .small { font-size: 8.4pt; color: var(--muted); }
.lead { font-size: 11pt; color: #39405C; }

/* cover */
.cover { page: first; height: 297mm; width: 210mm; position: relative; overflow: hidden; color: #fff; background: linear-gradient(155deg,#10163B 0%,#1B2559 45%,#2B3AA8 100%); break-after: page; }
.cover .art { position:absolute; inset:0; }
.cover .txt { position:absolute; left: 20mm; right: 20mm; top: 62mm; }
.cover .tag { letter-spacing: .28em; font-size: 9pt; color:#9FB0FF; font-weight:700; }
.cover h1 { color:#fff; font-size: 38pt; line-height:1.08; margin: 6mm 0 5mm; font-weight: 300; }
.cover h1 b { font-weight: 800; color:#7EE7DF; }
.cover .sub { font-size: 13pt; color:#C9D3FF; max-width: 135mm; line-height:1.45; }
.cover .meta { position:absolute; left:20mm; right:20mm; bottom: 20mm; display:flex; gap: 10mm; font-size: 9pt; color:#C9D3FF; border-top:1px solid #ffffff44; padding-top: 5mm; }
.cover .meta b { display:block; color:#fff; font-size: 10pt; }
.parts { position:absolute; left:20mm; top: 170mm; display:flex; gap: 4mm; }
.parts div { border:1px solid #ffffff55; border-radius: 3mm; padding: 3mm 4mm; font-size: 8.6pt; color:#E2E8FF; background:#ffffff14; width: 38mm; }
.parts b { display:block; color:#7EE7DF; font-size: 15pt; }

/* part dividers */
.part { page: part; height: 297mm; width: 210mm; background: linear-gradient(160deg,#10163B,#1B2559 60%,#2B3AA8); color:#fff; break-before: page; break-after: page; display:flex; align-items:center; }
.part-in { padding: 0 24mm; }
.part-num { letter-spacing:.3em; color:#7EE7DF; font-weight:700; font-size: 11pt; }
.part h1 { color:#fff; font-size: 34pt; font-weight: 300; margin: 6mm 0 6mm; line-height:1.1; }
.part-lead { color:#C9D3FF; font-size: 12.5pt; max-width: 130mm; }

/* toc */
.toc { break-after: page; }
.toc h2 { border:0; font-size: 22pt; }
.toc .r1 { font-weight:700; color: var(--navy); margin-top: 2mm; font-size: 10.5pt; display:flex; }
.toc .r2 { margin-left: 7mm; display:flex; color:#39405C; font-size: 8.8pt; line-height:1.35; }
.toc .dots { flex: 1; border-bottom: 1px dotted #AAB; margin: 0 3px 4px; }
.toc .pg { color: var(--indigo); font-weight:700; min-width: 8mm; text-align:right; }

/* tables */
table.t { width:100%; border-collapse: collapse; font-size: 8.5pt; margin: 2mm 0 4mm; break-inside: auto; }
table.t th { background: var(--navy); color:#fff; text-align:left; padding: 1.6mm 2mm; font-weight:600; font-size: 8.2pt; }
table.t td { padding: 1.4mm 2mm; border-bottom: 1px solid var(--line); vertical-align: top; }
table.t tr:nth-child(even) td { background: #F7F8FD; }
table.t tr { break-inside: avoid; }
table.t.tight td { padding: .9mm 1.6mm; font-size: 8pt; }
table.t td:first-child { font-weight: 600; color: var(--navy); }
.m { display:inline-block; font-size: 7.4pt; font-weight:800; padding: 0 5px; border-radius: 3px; color:#fff; font-family: Consolas, monospace; min-width: 13mm; text-align:center; }
.m.GET{background:#17A2A0}.m.POST{background:#4F5BD5}.m.PUT{background:#F2A33A}.m.PATCH{background:#7C5CD6}.m.DELETE{background:#E5484D}
.chip { display:inline-block; padding: 0 6px; border-radius: 8px; font-size: 7.6pt; font-weight:700; margin: 0 1px; }
.chip.pub{background:#FDF1DC;color:#7A4B05}.chip.ses{background:#E2F4EA;color:#17613F}.chip.perm{background:#EEF1FB;color:#2B3470}.chip.pend{background:#E3F6F5;color:#0B5F5D}.chip.opt{background:#EFEAFB;color:#3D2A8A}

/* figures */
figure.fig { margin: 3mm 0 4mm; break-inside: avoid; text-align:center; }
figure.fig figcaption { font-size: 8.2pt; color: var(--muted); margin-top: 1.5mm; text-align:center; }
svg.dg { width: 100%; height: auto; display:block; margin: 0 auto; }
img.chart { width: 100%; height: auto; display:block; margin: 0 auto; }
.win { border: 1px solid #C9D0EA; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px #1B255922; background:#fff; }
.win .bar { background:#E9ECF8; padding: 1.4mm 2mm; display:flex; align-items:center; gap: 3px; border-bottom:1px solid #D5DAF0; }
.win .bar i { width: 7px; height: 7px; border-radius: 50%; background:#C3CAE6; display:inline-block; }
.win .bar i:nth-child(1){background:#F28B82}.win .bar i:nth-child(2){background:#F2C94C}.win .bar i:nth-child(3){background:#6FCF97}
.win .bar span { margin-left: 8px; background:#fff; border-radius: 9px; padding: 0 10px; font: 7.4pt Consolas, monospace; color:#6B7390; flex:1; text-align:left; }
.win img { width: 100%; display:block; }
.two { display:grid; grid-template-columns: 1fr 1fr; gap: 4mm; } .two figcaption{grid-column:1/3}
.grid2 { display:grid; grid-template-columns: 1fr 1fr; gap: 5mm; align-items: start; }
.grid3 { display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }

/* callouts */
.co { display:flex; gap: 3mm; border-radius: 5px; padding: 2.5mm 3.5mm; margin: 3mm 0; font-size: 9pt; break-inside: avoid; border-left: 4px solid; }
.co .ci { font-weight: 800; width: 5mm; height: 5mm; border-radius: 50%; color:#fff; text-align:center; line-height:5mm; font-size: 8pt; flex: none; margin-top: 1px; }
.co.info{background:#EEF1FB;border-color:#4F5BD5}.co.info .ci{background:#4F5BD5}
.co.warn{background:#FDF1DC;border-color:#F2A33A}.co.warn .ci{background:#E08A0B}
.co.ok{background:#E2F4EA;border-color:#2E9E6B}.co.ok .ci{background:#2E9E6B}
.co.key{background:#EFEAFB;border-color:#7C5CD6}.co.key .ci{background:#7C5CD6}

/* kpis */
.kpis { display:grid; grid-template-columns: repeat(4,1fr); gap: 3mm; margin: 3mm 0 4mm; }
.kpi { border:1px solid var(--line); border-radius: 6px; padding: 3mm; background: linear-gradient(180deg,#fff,#F5F7FE); text-align:center; }
.kv { font-size: 21pt; font-weight: 800; line-height:1.1; } .kl { font-size: 8pt; color: var(--muted); }

/* steps */
ol.steps { list-style:none; padding:0; counter-reset: s; margin: 2mm 0 3mm; }
ol.steps li { counter-increment: s; position: relative; padding: 0 0 2mm 9mm; border-left: 2px solid #C9D0EA; margin-left: 3.5mm; }
ol.steps li::before { content: counter(s); position:absolute; left: -3.9mm; top: 0; width: 6mm; height: 6mm; border-radius:50%; background: var(--indigo); color:#fff; font-weight:700; font-size: 8pt; text-align:center; line-height: 6mm; }
ol.steps li:last-child { border-color: transparent; }
.pb { break-before: page; }
.nb { break-inside: avoid; }
.src { font-size: 7.6pt; color: var(--muted); }
"""
