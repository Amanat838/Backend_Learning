"""Build the course book: Markdown chapters -> styled HTML -> PDF (headless Chrome).

Usage:  python book/build.py
Output: Backend-Book-1-Foundations.pdf in the repo root.

Two passes: the first render finds the page each chapter starts on (via hidden
markers), the second render writes those page numbers into the table of contents.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
OUT_PDF = ROOT.parent / "Backend-Book-1-Foundations.pdf"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

MD_EXTENSIONS = [
    "tables",
    "admonition",
    "md_in_html",
    "attr_list",
    "sane_lists",
    "toc",
]
MD_CONFIG = {
    "toc": {"permalink": False},
}

FENCE_RE = re.compile(
    r"^(?P<indent>[ \t]*)```(?P<lang>[\w+-]*)[ \t]*\n(?P<code>.*?)^(?P=indent)```[ \t]*$",
    re.M | re.S,
)
_FORMATTER = HtmlFormatter(cssclass="hl", nowrap=False)


def highlight_block(lang: str, code: str) -> str:
    if lang in ("output", "text", ""):
        cls = "hl term" if lang == "output" else "hl"
        return f'<div class="{cls}"><pre>{html.escape(code)}</pre></div>'
    try:
        lexer = get_lexer_by_name(lang)
    except ClassNotFound:
        lexer = TextLexer()
    return highlight(code, lexer, _FORMATTER)


def stash_code(text: str) -> tuple[str, dict[str, str]]:
    """Replace fenced blocks (at any indentation, e.g. inside callouts) with tokens.

    Python-Markdown can't nest fenced code inside admonitions, so we highlight the
    code ourselves and swap it back in after Markdown has run.
    """
    stash: dict[str, str] = {}

    def repl(m: re.Match[str]) -> str:
        indent = m.group("indent")
        lines = m.group("code").rstrip("\n").split("\n")
        code = "\n".join(line[len(indent):] if line.startswith(indent) else line.lstrip() for line in lines)
        token = f"CODEBLOCKTOKEN{len(stash):04d}"
        stash[token] = highlight_block(m.group("lang").lower(), code)
        return f"{indent}{token}"

    return FENCE_RE.sub(repl, text), stash


def unstash_code(html_text: str, stash: dict[str, str]) -> str:
    for token, block in stash.items():
        html_text = html_text.replace(f"<p>{token}</p>", block).replace(token, block)
    return html_text


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4)
        for line in text[4:end].splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("\"")
        text = text[end + 5 :]
    return meta, text


def marker(n: int) -> str:
    return f'<span class="pdf-marker">QQMARK{n:03d}QQ</span>'


def render_sections() -> tuple[str, list[dict]]:
    """Render every source file. Returns body HTML and TOC entries."""
    toc: list[dict] = []
    parts: list[str] = []
    for path in sorted(SRC.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        kind = meta.get("kind", "chapter")
        md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)
        # Allow "text {: .done }" on one line: attr_list needs it on its own line.
        body = re.sub(r"^([ \t]*)(\S.*?)[ \t]+(\{:[^}]*\})[ \t]*$", r"\1\2\n\1\3", body, flags=re.M)
        body, stash = stash_code(body)
        body_html = unstash_code(md.convert(body), stash)
        idx = len(toc)
        anchor = f"sec-{idx:03d}"

        if kind == "raw":  # cover, toc placeholder, etc.
            parts.append(body_html)
            continue

        title = meta.get("title", path.stem)
        entry = {"kind": kind, "title": title, "anchor": anchor, "num": meta.get("num", ""),
                 "label": meta.get("label", ""), "hide": meta.get("toc", "") == "hide"}
        toc.append(entry)

        if kind == "part":
            parts.append(
                f'<section class="part-page" id="{anchor}">{marker(idx)}'
                f'<div class="part-label">{html.escape(meta.get("label", ""))}</div>'
                f'<h1 class="part-title">{html.escape(title)}</h1>'
                f'<div class="part-sub">{html.escape(meta.get("subtitle", ""))}</div>'
                f'<div class="part-body">{body_html}</div></section>'
            )
        else:
            label = {
                "chapter": f"Chapter {meta.get('num', '')}",
                "project": "Project",
                "appendix": f"Appendix {meta.get('num', '')}",
                "front": meta.get("label", ""),
            }.get(kind, "")
            meta_line = " · ".join(v for v in (meta.get("phase", ""), meta.get("time", "")) if v)
            parts.append(
                f'<section class="chapter {kind}" id="{anchor}">{marker(idx)}'
                f'<header class="chapter-head"><div class="chapter-label">{html.escape(label)}</div>'
                f'<h1 class="chapter-title">{html.escape(title)}</h1>'
                + (f'<div class="chapter-meta">{html.escape(meta_line)}</div>' if meta_line else "")
                + f"</header>{body_html}</section>"
            )
    return "\n".join(parts), toc


def toc_html(toc: list[dict], pages: dict[str, int]) -> str:
    rows = []
    for e in toc:
        if e["hide"]:
            continue
        page = pages.get(e["anchor"], 0)
        page_txt = str(page) if page else "00"
        if e["kind"] == "part":
            rows.append(
                f'<a class="toc-part" href="#{e["anchor"]}"><span>{html.escape(e["label"])} · {html.escape(e["title"])}</span>'
                f'<span class="toc-page">{page_txt}</span></a>'
            )
        else:
            prefix = {
                "chapter": f'<span class="toc-num">{e["num"]}</span>',
                "appendix": f'<span class="toc-num">{e["num"]}</span>',
                "project": '<span class="toc-num toc-proj">P</span>',
                "front": '<span class="toc-num"></span>',
            }[e["kind"]]
            rows.append(
                f'<a class="toc-row toc-{e["kind"]}" href="#{e["anchor"]}">{prefix}'
                f'<span class="toc-title">{html.escape(e["title"])}</span><span class="toc-dots"></span>'
                f'<span class="toc-page">{page_txt}</span></a>'
            )
    return '<div class="toc-list">' + "\n".join(rows) + "</div>"


def build_html(pages: dict[str, int]) -> Path:
    body, toc = render_sections()
    body = body.replace("<!--TOC-->", toc_html(toc, pages))
    css = (ROOT / "style.css").read_text(encoding="utf-8")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Backend Engineering: Zero to Hired, Book 1</title>
<style>{css}</style></head>
<body>{body}</body></html>"""
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "book.html"
    out.write_text(doc, encoding="utf-8")
    return out


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    profile = BUILD / "chrome-profile"
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-pdf-header-footer",
        "--generate-pdf-document-outline",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    if not pdf_path.exists():
        sys.exit("Chrome did not produce a PDF")


def find_pages(pdf_path: Path, toc: list[dict]) -> dict[str, int]:
    reader = PdfReader(str(pdf_path))
    found: dict[str, int] = {}
    for i, page in enumerate(reader.pages, start=1):
        for m in re.findall(r"QQMARK(\d{3})QQ", page.extract_text() or ""):
            idx = int(m)
            if idx < len(toc):
                found.setdefault(toc[idx]["anchor"], i)
    return found


def fix_outline(pdf_path: Path, html_path: Path) -> None:
    """Chrome builds bookmarks from rendered lines, so wrapped headings lose a space
    ("SolveProblems"). Restore the real heading text by matching without whitespace."""
    headings = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html_path.read_text(encoding="utf-8"), re.S)
    real = {}
    for h in headings:
        text = html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
        real[re.sub(r"\s+", "", text)] = text

    writer = PdfWriter(clone_from=str(pdf_path))

    def walk(node) -> None:
        while node is not None:
            item = node.get_object()
            title = str(item.get("/Title", ""))
            fixed = real.get(re.sub(r"\s+", "", title))
            if fixed and fixed != title:
                item[NameObject("/Title")] = TextStringObject(fixed)
            if "/First" in item:
                walk(item["/First"])
            node = item.get("/Next")

    root = writer._root_object.get("/Outlines")
    if root is not None and "/First" in root.get_object():
        walk(root.get_object()["/First"])
    writer.add_metadata({"/Title": "Backend Engineering: Zero to Hired, Book 1", "/Author": "Claude, for Syed Amanat Ali Shah"})
    with open(pdf_path, "wb") as f:
        writer.write(f)


def main() -> None:
    _, toc = render_sections()
    tmp_pdf = BUILD / "pass1.pdf"
    BUILD.mkdir(exist_ok=True)
    print_pdf(build_html({}), tmp_pdf)
    pages = find_pages(tmp_pdf, toc)
    missing = [e["title"] for e in toc if e["anchor"] not in pages]
    if missing:
        print("WARNING: no page found for:", missing)
    html_path = build_html(pages)
    print_pdf(html_path, OUT_PDF)
    fix_outline(OUT_PDF, html_path)
    # Verify the second pass didn't shift anything.
    if find_pages(OUT_PDF, toc) != pages:
        print("WARNING: page numbers shifted between passes")
    n = len(PdfReader(str(OUT_PDF)).pages)
    print(f"Wrote {OUT_PDF} ({n} pages)")


if __name__ == "__main__":
    main()
