#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "posts" / "effective-resistance-rewiring"
MARKDOWN_PATH = POST_DIR / "post.md"
BIB_PATH = POST_DIR / "_bibliography" / "papers.bib"
OUTPUT_PATH = POST_DIR / "index.html"


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
      return {}, text
    _, rest = text.split("---\n", 1)
    front_matter_text, body = rest.split("\n---\n", 1)
    data: dict[str, str] = {}
    for line in front_matter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body.lstrip()


def parse_bib_entries(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    chunks = re.split(r"(?=@\w+\{)", text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        match = re.match(r"@(\w+)\{([^,]+),", chunk)
        if not match:
            continue
        entry_type, key = match.groups()
        fields: dict[str, str] = {"ENTRYTYPE": entry_type}
        for field, value in re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|(?:\{[^{}]*\}))*)\}", chunk, flags=re.S):
            fields[field.lower()] = " ".join(value.replace("\n", " ").split())
        entries[key] = fields
    return entries


def strip_latex_accents(value: str) -> str:
    replacements = {
        r"\'a": "á", r"\'e": "é", r"\'i": "í", r"\'o": "ó", r"\'u": "ú",
        r"\`a": "à", r"\`e": "è", r"\`i": "ì", r"\`o": "ò", r"\`u": "ù",
        r'\"o': "ö", r"\'A": "Á", r"\'E": "É", r"\'I": "Í", r"\'O": "Ó", r"\'U": "Ú",
        r"\~n": "ñ", r"\c{c}": "ç", r"\v{c}": "č", r"\v{s}": "š", r"\l": "ł",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"[{}]", "", value)
    return value


def format_authors(raw: str) -> str:
    authors = [strip_latex_accents(part.strip()) for part in raw.split(" and ") if part.strip()]
    return ", ".join(authors)


def format_reference(entry: dict[str, str]) -> str:
    parts = []
    authors = entry.get("author")
    if authors:
        parts.append(format_authors(authors))
    title = entry.get("title")
    if title:
        parts.append(f'"{strip_latex_accents(title)}"')
    venue = entry.get("journal") or entry.get("booktitle") or entry.get("publisher")
    if venue:
        parts.append(strip_latex_accents(venue))
    year = entry.get("year")
    if year:
        parts.append(year)
    note = entry.get("note")
    if note:
        parts.append(strip_latex_accents(note))
    return ". ".join(parts) + "."


def replace_citations(text: str, bibliography: dict[str, dict[str, str]]) -> tuple[str, list[str]]:
    citation_order: list[str] = []

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in citation_order:
            citation_order.append(key)
        number = citation_order.index(key) + 1
        label = bibliography.get(key, {}).get("title", key)
        return f'<a class="citation" href="#ref-{key}" title="{html.escape(strip_latex_accents(label))}">[{number}]</a>'

    updated = re.sub(r'<d-cite key="([^"]+)"></d-cite>', repl, text)
    return updated, citation_order


def render_bibliography(keys: list[str], bibliography: dict[str, dict[str, str]]) -> str:
    items = []
    for index, key in enumerate(keys, start=1):
        entry = bibliography.get(key)
        if entry is None:
            items.append(f'<li id="ref-{html.escape(key)}">Missing bibliography entry for {html.escape(key)}.</li>')
            continue
        items.append(f'<li id="ref-{html.escape(key)}"><span class="ref-index">[{index}]</span> {html.escape(format_reference(entry))}</li>')
    return '<ol class="references-list">\n' + "\n".join(items) + "\n</ol>"


def convert_inline(text: str) -> str:
    parts = re.split(r"(<[^>]+>)", text)
    converted: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("<") and part.endswith(">"):
            converted.append(part)
            continue
        part = html.escape(part, quote=False)
        part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
        part = re.sub(r"`([^`]+)`", r"<code>\1</code>", part)
        converted.append(part)
    return "".join(converted)


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    blockquote_open = False
    html_block = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{convert_inline(' '.join(paragraph).strip())}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type == "ul":
            output.append("</ul>")
        elif list_type == "ol":
            output.append("</ol>")
        list_type = None

    def close_blockquote() -> None:
        nonlocal blockquote_open
        if blockquote_open:
            output.append("</blockquote>")
            blockquote_open = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if html_block:
            output.append(line)
            if stripped.startswith("</div>"):
                html_block = False
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            close_blockquote()
            continue

        if stripped.startswith("<div"):
            flush_paragraph()
            close_list()
            close_blockquote()
            output.append(line)
            html_block = True
            continue

        if stripped.startswith("<") and stripped.endswith(">") and not stripped.startswith("<d-bibliography"):
            flush_paragraph()
            close_list()
            close_blockquote()
            output.append(line)
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            close_blockquote()
            output.append(f"<h2>{convert_inline(stripped[3:])}</h2>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            close_blockquote()
            if list_type != "ul":
                close_list()
                output.append("<ul>")
                list_type = "ul"
            output.append(f"<li>{convert_inline(stripped[2:])}</li>")
            continue

        ordered_match = re.match(r"(\d+)\.\s+(.*)", stripped)
        if ordered_match:
            flush_paragraph()
            close_blockquote()
            if list_type != "ol":
                close_list()
                output.append("<ol>")
                list_type = "ol"
            output.append(f"<li>{convert_inline(ordered_match.group(2))}</li>")
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            close_list()
            if not blockquote_open:
                output.append("<blockquote>")
                blockquote_open = True
            output.append(f"<p>{convert_inline(stripped[2:])}</p>")
            continue

        if stripped == "<d-bibliography></d-bibliography>":
            flush_paragraph()
            close_list()
            close_blockquote()
            output.append("__BIBLIOGRAPHY__")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    close_list()
    close_blockquote()
    return "\n".join(output)


def build() -> None:
    front_matter, markdown_body = parse_front_matter(MARKDOWN_PATH.read_text(encoding="utf-8"))
    bibliography = parse_bib_entries(BIB_PATH.read_text(encoding="utf-8"))
    with_citations, citation_order = replace_citations(markdown_body, bibliography)
    article_html = markdown_to_html(with_citations)
    article_html = article_html.replace("__BIBLIOGRAPHY__", render_bibliography(citation_order, bibliography))

    title = front_matter.get("title", "Post")
    description = front_matter.get("description", "")
    date = front_matter.get("date", "")

    output = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{html.escape(description)}" />
  <meta name="theme-color" content="#07111f" />
  <title>{html.escape(title)} | Bertran Miquel Oliver</title>
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml" />
  <link rel="alternate icon" href="../../flavicon.ico" type="image/x-icon" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    :root {{
      color-scheme: dark;
      --bg: #07111f;
      --bg-soft: #0d1b2e;
      --surface: rgba(255,255,255,0.08);
      --surface-strong: rgba(255,255,255,0.13);
      --text: #f6f8fb;
      --muted: #aab7c8;
      --line: rgba(255,255,255,0.16);
      --accent: #44d7b6;
      --accent-strong: #6be4ff;
      --shadow: 0 24px 80px rgba(0,0,0,0.35);
      --radius-lg: 16px;
      --max: 900px;
    }}
    body.light-theme {{
      color-scheme: light;
      --bg: #f7fafc;
      --bg-soft: #eef4f8;
      --surface: rgba(255,255,255,0.82);
      --surface-strong: #ffffff;
      --text: #101827;
      --muted: #516071;
      --line: rgba(15,23,42,0.13);
      --shadow: 0 24px 70px rgba(33,55,85,0.14);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 18% 8%, rgba(68, 215, 182, 0.16), transparent 30%),
        radial-gradient(circle at 86% 24%, rgba(107, 228, 255, 0.12), transparent 26%),
        linear-gradient(135deg, var(--bg), var(--bg-soft));
      color: var(--text);
      font-family: Inter, system-ui, sans-serif;
      line-height: 1.7;
      transition: background 220ms ease, color 220ms ease;
    }}
    a {{ color: var(--accent-strong); }}
    img {{ display: block; max-width: 100%; }}
    .shell {{ width: min(var(--max), calc(100% - 28px)); margin: 0 auto; }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 22px 0 0;
    }}
    .back-link {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      text-decoration: none;
      font-weight: 700;
    }}
    .theme-toggle {{
      display: inline-grid;
      place-items: center;
      min-width: 64px;
      height: 42px;
      padding: 0 13px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--surface);
      color: var(--text);
      cursor: pointer;
      font: inherit;
      font-size: 0.78rem;
      font-weight: 800;
      transition: transform 180ms ease, background 180ms ease, border-color 180ms ease;
    }}
    .theme-toggle:hover {{
      transform: translateY(-2px);
      background: var(--surface-strong);
      border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
    }}
    .article {{
      padding: 34px 0 80px;
    }}
    .article-header {{
      margin-bottom: 34px;
      padding: 32px;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      margin: 0 0 12px;
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{
      margin-bottom: 18px;
      font-size: clamp(2.6rem, 6vw, 4.8rem);
      line-height: 0.98;
    }}
    h2 {{
      margin: 44px 0 18px;
      font-size: clamp(1.5rem, 3vw, 2.3rem);
      line-height: 1.1;
    }}
    .article-header p:last-child {{ margin-bottom: 0; }}
    .post-info {{
      margin: 24px 0 24px;
      padding: 18px 20px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(255,255,255,0.04);
      color: var(--muted);
    }}
    .content {{
      padding: 0 4px;
    }}
    .content p, .content li, .content blockquote {{
      color: var(--text);
      font-size: 1.02rem;
    }}
    .content ul, .content ol {{
      padding-left: 22px;
    }}
    .content li {{
      margin-bottom: 10px;
    }}
    .content blockquote {{
      margin: 28px 0;
      padding: 2px 0 2px 18px;
      border-left: 3px solid var(--accent);
      color: var(--muted);
    }}
    .content code {{
      padding: 0.1em 0.35em;
      border-radius: 6px;
      background: rgba(255,255,255,0.08);
      font-size: 0.95em;
    }}
    .citation {{
      text-decoration: none;
      font-weight: 700;
      white-space: nowrap;
    }}
    .row {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin: 28px 0 14px;
    }}
    .caption {{
      margin: 0 0 28px;
      color: var(--muted);
      font-size: 0.95rem;
      text-align: center;
    }}
    .references-list {{
      padding-left: 24px;
    }}
    .references-list li {{
      margin-bottom: 14px;
      color: var(--muted);
    }}
    .ref-index {{
      color: var(--accent);
      font-weight: 800;
    }}
    .footer {{
      padding: 24px 0 44px;
      color: var(--muted);
      border-top: 1px solid var(--line);
    }}
    @media (max-width: 720px) {{
      .topbar {{
        gap: 12px;
      }}
      .article-header {{ padding: 24px; }}
      .row {{ grid-template-columns: 1fr; }}
    }}
  </style>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head>
<body>
  <div class="shell topbar">
    <a class="back-link" href="../../index.html">← Back to homepage</a>
    <button class="theme-toggle" id="themeToggle" type="button" aria-label="Toggle color theme">Theme</button>
  </div>
  <main class="shell article">
    <header class="article-header">
      <p class="eyebrow">Blog Post · {html.escape(date)}</p>
      <h1>{html.escape(title)}</h1>
      <p>{html.escape(description)}</p>
    </header>
    <article class="content">
{article_html}
    </article>
  </main>
  <footer class="shell footer">
    <p>Bertran Miquel Oliver · Graph structure, GNNs, and AI for biological data</p>
  </footer>
  <script>
    const themeToggle = document.getElementById('themeToggle');
    const storedTheme = localStorage.getItem('theme');
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;

    if (storedTheme === 'light' || (!storedTheme && prefersLight)) {{
      document.body.classList.add('light-theme');
    }}

    function updateThemeLabel() {{
      const isLight = document.body.classList.contains('light-theme');
      themeToggle?.setAttribute('aria-label', isLight ? 'Switch to dark theme' : 'Switch to light theme');
    }}

    updateThemeLabel();

    themeToggle?.addEventListener('click', () => {{
      document.body.classList.toggle('light-theme');
      localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
      updateThemeLabel();
    }});
  </script>
</body>
</html>
"""
    OUTPUT_PATH.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    build()
