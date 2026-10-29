"""Assemble the guide: HTML -> PDF via headless Chrome (puppeteer-core), TOC page numbers filled in a second pass."""
import json, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import base
import part_a, part_b, part_c

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "CFA_LMS_Platform_Technical_Guide.pdf"
NODE_PP = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None  # dir containing node_modules/puppeteer-core


def assemble(pages=None):
    base.HEADINGS.clear(); base._fig["n"] = 0
    body_a = part_a.build(); body_b = part_b.build(); body_c = part_c.build()
    toc = part_a.toc(pages)
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>CFA Learning Hub · Platform Technical Guide</title>'
            f'<style>{base.CSS}</style></head><body>{part_a.cover()}{toc}{body_a}{body_b}{body_c}</body></html>')
    return html


def render(html_path, pdf_path):
    js = f"""
const puppeteer=require('puppeteer-core');
(async()=>{{
 const b=await puppeteer.launch({{executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:'new',args:['--no-sandbox']}});
 const p=await b.newPage();
 await p.goto('file:///{html_path.as_posix()}',{{waitUntil:'load',timeout:120000}});
 await new Promise(r=>setTimeout(r,1500));
 await p.pdf({{path:'{pdf_path.as_posix()}',preferCSSPageSize:true,printBackground:true,outline:true,tagged:true,timeout:240000}});
 await b.close();
}})().catch(e=>{{console.error(e);process.exit(1)}});
"""
    f = NODE_PP / "render.js"
    f.write_text(js, encoding="utf8")
    subprocess.run(["node", str(f)], check=True, cwd=NODE_PP)


def page_numbers(pdf_path):
    from pypdf import PdfReader
    r = PdfReader(str(pdf_path))
    texts = [(pg.extract_text() or "") for pg in r.pages]
    res = {}
    start = 2  # skip cover and TOC (physical pages 0,1..)
    toc_end = next((i for i, t in enumerate(texts) if "PART 0" in t), 2)
    for lvl, num, title, hid in base.HEADINGS:
        plain = re.sub(r"<[^>]+>", "", title).replace("&amp;", "&")
        key = plain[:28]
        for i in range(toc_end, len(texts)):
            t = " ".join(texts[i].split())
            if lvl == 1:
                if re.search(rf"PART{num}(?!\d)", re.sub(r"\s", "", t)): res[hid] = i + 1; break
            else:
                if re.search(rf"\b{re.escape(num)}\s*{re.escape(key[:16])}", t): res[hid] = i + 1; break
    return res, len(r.pages)


if __name__ == "__main__":
    html_path = HERE / "guide.html"; tmp_pdf = HERE / "pass1.pdf"
    html_path.write_text(assemble(), encoding="utf8")
    render(html_path, tmp_pdf)
    pages, n = page_numbers(tmp_pdf)
    print("pass1 pages", n, "headings found", len(pages), "of", len(base.HEADINGS))
    html_path.write_text(assemble(pages), encoding="utf8")
    render(html_path, OUT)
    pages2, n2 = page_numbers(OUT)
    print("pass2 pages", n2, "match", pages2 == pages)
