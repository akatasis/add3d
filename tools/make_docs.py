#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build docs/index.html from add.py's own docstrings plus docs/content.py.

    python3 tools/make_docs.py

The reference section is generated from the source, so it cannot drift away
from the code.  The prose and the Lithuanian translations live in
docs/content.py.
"""

import ast
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "docs"))
sys.path.insert(0, ROOT)

import content                                                    # noqa: E402

SOURCE = os.path.join(ROOT, "add.py")
OUTPUT = os.path.join(ROOT, "docs", "index.html")

SECTION_RE = re.compile(r"^#\s+(\d+)\.\s+(.+?)\s*$")

sys.path.insert(0, os.path.join(ROOT, "tools"))
import coverage                                              # noqa: E402


# ---------------------------------------------------------------------------
#  reading add.py
# ---------------------------------------------------------------------------

def read_api():
    """Return [(section title, [entry, ...]), ...] read out of add.py."""
    with open(SOURCE, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    # Section headers look like:   #  5. Flat shapes   (inside a #==== block)
    headers = []
    for i, line in enumerate(lines):
        m = SECTION_RE.match(line.strip())
        if m and i and lines[i - 1].startswith("# ====="):
            headers.append((i + 1, "%s. %s" % (m.group(1), m.group(2))))

    def section_of(lineno):
        title = "0. Constants"
        for start, name in headers:
            if start <= lineno:
                title = name
        return title

    tree = ast.parse(text)
    public = set(_public_names(text))
    groups = {}
    order = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name.startswith("_") or node.name not in public:
                continue
            entry = {
                "name": node.name,
                "signature": _signature(node),
                "doc": ast.get_docstring(node) or "",
                "kind": "class" if isinstance(node, ast.ClassDef) else "function",
            }
        elif isinstance(node, ast.Assign):
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id not in public:
                continue
            if target.id.startswith("_"):
                continue
            entry = {"name": target.id, "signature": "",
                     "doc": _comment_above(lines, node.lineno), "kind": "value"}
        else:
            continue
        title = section_of(node.lineno)
        if title not in groups:
            groups[title] = []
            order.append(title)
        groups[title].append(entry)

    # aliases assigned as `ball = sphere` land in the compatibility section
    return [(title, groups[title]) for title in order]


def _comment_above(lines, lineno):
    """The ``#:`` comment block just above a module-level assignment."""
    out = []
    i = lineno - 2
    while i >= 0 and lines[i].strip().startswith("#:"):
        out.insert(0, lines[i].strip()[2:].strip())
        i -= 1
    return " ".join(out)


def _public_names(text):
    namespace = {}
    exec(compile(text, SOURCE, "exec"), namespace)          # noqa: S102
    return namespace["__all__"]


def _signature(node):
    if isinstance(node, ast.ClassDef):
        return ""
    a = node.args
    names = [arg.arg for arg in a.args]
    defaults = [None] * (len(names) - len(a.defaults)) + list(a.defaults)
    parts = []
    for name, default in zip(names, defaults):
        if default is None:
            parts.append(name)
        else:
            parts.append("%s=%s" % (name, _literal(default)))
    if a.vararg:
        parts.append("*" + a.vararg.arg)
    if a.kwarg:
        parts.append("**" + a.kwarg.arg)
    return "(%s)" % ", ".join(parts)


def _literal(node):
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        return ast.unparse(node) if hasattr(ast, "unparse") else "..."
    if isinstance(value, float) and abs(value - 6.283185307179586) < 1e-12:
        return "2*pi"
    if isinstance(value, str):
        return '"%s"' % value
    return repr(value)


# ---------------------------------------------------------------------------
#  tiny markdown
# ---------------------------------------------------------------------------

def inline(text):
    text = html.escape(text, quote=False)
    # Sphinx-style roles such as :func:`name` -- keep the name, drop the role.
    text = re.sub(r":(?:func|data|class|meth|mod|attr):`~?([^`]+)`",
                  r"``\1``", text)
    text = re.sub(r"``([^`]+)``", r"<code>\1</code>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<!-)--(?!-)", "&mdash;", text)
    return text


def markdown(source):
    """A very small Markdown subset: enough for this one page."""
    out = []
    lines = source.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            out.append('<pre class="code"><button class="copy" '
                       'title="copy">&#128203;</button><code>%s</code></pre>'
                       % html.escape("\n".join(block)))
            continue

        if stripped.startswith("!"):
            src, _, caption = stripped[1:].partition("|")
            out.append('<figure><img loading="lazy" src="images/%s" alt="%s">'
                       '<figcaption>%s</figcaption></figure>'
                       % (src, html.escape(caption), inline(caption)))
            i += 1
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            out.append("<h%d>%s</h%d>" % (level + 1,
                                          inline(stripped[level:].strip()),
                                          level + 1))
            i += 1
            continue

        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in
                             lines[i].strip().strip("|").split("|")])
                i += 1
            head = rows[0]
            body = [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            table = ["<table><thead><tr>"]
            table += ["<th>%s</th>" % inline(c) for c in head]
            table.append("</tr></thead><tbody>")
            for r in body:
                table.append("<tr>%s</tr>"
                             % "".join("<td>%s</td>" % inline(c) for c in r))
            table.append("</tbody></table>")
            out.append("".join(table))
            continue

        if not stripped:
            i += 1
            continue

        para = []
        while i < len(lines) and lines[i].strip() \
                and not lines[i].strip().startswith(("#", "```", "|", "!")):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
    return "\n".join(out)


def docstring_html(doc, skip_summary=True):
    """Render a function docstring: paragraphs, and `::` blocks as code.

    The first line is already shown as the summary, so it is left out here.
    """
    if not doc:
        return ""
    lines = doc.split("\n")
    if skip_summary:
        while lines and lines[0].strip():
            lines.pop(0)
    if not any(l.strip() for l in lines):
        return ""
    out = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        indent = len(lines[i]) - len(lines[i].lstrip())
        if indent >= 4:
            block = []
            while i < len(lines) and (not lines[i].strip()
                                      or len(lines[i]) - len(lines[i].lstrip())
                                      >= 4):
                block.append(lines[i][4:])
                i += 1
            while block and not block[-1].strip():
                block.pop()
            out.append('<pre class="code"><button class="copy" '
                       'title="copy">&#128203;</button><code>%s</code></pre>'
                       % html.escape("\n".join(block)))
            continue
        para = []
        while i < len(lines) and lines[i].strip() \
                and len(lines[i]) - len(lines[i].lstrip()) < 4:
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        text = re.sub(r"::$", ":", text)
        out.append("<p>%s</p>" % inline(text))
    return "\n".join(out)


# ---------------------------------------------------------------------------
#  the page
# ---------------------------------------------------------------------------

CSS = """
:root{
  --bg:#ffffff; --fg:#1b1d21; --muted:#5d6470; --line:#e2e5ea;
  --accent:#8a4b1e; --accent-soft:#f6efe8; --code-bg:#f6f7f9;
  --card:#fbfbfc; --shadow:0 1px 2px rgba(0,0,0,.05);
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
}
:root:not([data-theme="light"]){
  @media (prefers-color-scheme: dark){
    --bg:#15171a; --fg:#e7e9ec; --muted:#9aa2ae; --line:#292d33;
    --accent:#e0a271; --accent-soft:#25201b; --code-bg:#1d2025;
    --card:#191c20; --shadow:0 1px 2px rgba(0,0,0,.3);
  }
}
:root[data-theme="dark"]{
  --bg:#15171a; --fg:#e7e9ec; --muted:#9aa2ae; --line:#292d33;
  --accent:#e0a271; --accent-soft:#25201b; --code-bg:#1d2025;
  --card:#191c20; --shadow:0 1px 2px rgba(0,0,0,.3);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);
  font-size:16px;line-height:1.65;-webkit-text-size-adjust:100%}
header{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.bar{max-width:1140px;margin:0 auto;padding:10px 16px;display:flex;
  align-items:center;gap:14px;flex-wrap:wrap}
.brand{font-family:var(--mono);font-weight:600;font-size:17px;color:var(--fg);
  text-decoration:none;white-space:nowrap}
.brand span{color:var(--accent)}
nav{display:flex;gap:2px;flex-wrap:wrap;flex:1;min-width:0}
nav a{color:var(--muted);text-decoration:none;font-size:14px;padding:5px 9px;
  border-radius:6px;white-space:nowrap}
nav a:hover{background:var(--accent-soft);color:var(--accent)}
.toggle{display:flex;border:1px solid var(--line);border-radius:7px;overflow:hidden}
.toggle button{font:inherit;font-size:13px;padding:4px 11px;border:0;cursor:pointer;
  background:transparent;color:var(--muted)}
.toggle button[aria-pressed="true"]{background:var(--accent);color:#fff}
main{max-width:1140px;margin:0 auto;padding:0 16px 96px}
.hero{padding:48px 0 24px;border-bottom:1px solid var(--line)}
.hero h1{font-size:clamp(30px,6vw,46px);margin:0 0 6px;letter-spacing:-.02em}
.hero h1 span{color:var(--accent);font-family:var(--mono)}
.hero p.lead{font-size:clamp(17px,2.4vw,21px);color:var(--muted);margin:0 0 20px;
  max-width:62ch}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.badge{font-size:12.5px;font-family:var(--mono);border:1px solid var(--line);
  border-radius:20px;padding:3px 11px;color:var(--muted);background:var(--card)}
section{padding-top:40px}
.used{font-size:.86em;color:#6b6b6b;margin-top:10px}
h2{font-size:clamp(23px,3.6vw,30px);margin:8px 0 12px;letter-spacing:-.01em}
h3{font-size:19px;margin:28px 0 8px}
h4{font-size:16px;margin:20px 0 6px;color:var(--muted)}
p{margin:0 0 14px;max-width:74ch}
a{color:var(--accent)}
code{font-family:var(--mono);font-size:.885em;background:var(--code-bg);
  padding:1.5px 5px;border-radius:4px;border:1px solid var(--line)}
pre.code{position:relative;background:var(--code-bg);border:1px solid var(--line);
  border-radius:9px;padding:14px 16px;overflow:auto;margin:0 0 16px;font-size:13.5px}
pre.code code{background:none;border:0;padding:0;font-size:inherit;line-height:1.6}
pre.code .copy{position:absolute;top:7px;right:7px;border:1px solid var(--line);
  background:var(--bg);color:var(--muted);border-radius:6px;cursor:pointer;
  font-size:11px;padding:3px 7px;opacity:0;transition:opacity .15s}
pre.code:hover .copy{opacity:1}
figure{margin:20px 0;border:1px solid var(--line);border-radius:11px;
  overflow:hidden;background:var(--card)}
figure img{display:block;width:100%;height:auto}
section > div > figure img{max-height:470px;object-fit:contain;
  background:#fafafa}
figcaption{font-size:13.5px;color:var(--muted);padding:9px 14px;
  border-top:1px solid var(--line)}
table{border-collapse:collapse;width:100%;margin:0 0 18px;font-size:14.5px;
  display:block;overflow-x:auto}
th,td{text-align:left;padding:7px 12px;border-bottom:1px solid var(--line);
  vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:13px;text-transform:uppercase;
  letter-spacing:.04em}
.gallery{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(310px,1fr))}
.gallery figure{margin:0}
.gallery figcaption b{display:block;color:var(--fg);font-family:var(--mono);
  font-size:12.5px;font-weight:600;margin-bottom:3px}
.tools{display:flex;gap:10px;align-items:center;margin:16px 0 22px;flex-wrap:wrap}
input[type=search]{flex:1;min-width:210px;font:inherit;font-size:14.5px;
  padding:8px 13px;border:1px solid var(--line);border-radius:8px;
  background:var(--bg);color:var(--fg)}
.api-group{margin-bottom:30px}
.api-group>h3{border-bottom:1px solid var(--line);padding-bottom:6px}
.fn{border:1px solid var(--line);border-radius:10px;margin:0 0 9px;
  background:var(--card);box-shadow:var(--shadow);overflow:hidden}
.fn>summary,.fn .head{cursor:pointer;padding:9px 14px;list-style:none;display:flex;
  gap:10px;align-items:baseline;flex-wrap:wrap}
.fn.flat .head{cursor:default;padding-left:33px}
.fn>summary::-webkit-details-marker{display:none}
.fn>summary::before{content:"\\25B8";color:var(--muted);font-size:11px;
  transition:transform .15s;display:inline-block}
.fn[open]>summary::before{transform:rotate(90deg)}
.fn .nm{font-family:var(--mono);font-weight:600;color:var(--accent)}
.fn .sig{font-family:var(--mono);font-size:13px;color:var(--muted);
  word-break:break-word}
.fn .sum{font-size:14px;color:var(--muted);flex-basis:100%;margin-left:19px}
.fn .body{padding:2px 14px 12px 33px;border-top:1px solid var(--line)}
.fn .body p{font-size:14.5px}
.fn .body pre.code{font-size:13px}
footer{border-top:1px solid var(--line);margin-top:56px;padding:26px 0;
  color:var(--muted);font-size:13.5px}
[data-lang="en"] .only-lt{display:none}
[data-lang="lt"] .only-en{display:none}
.note{background:var(--accent-soft);border-left:3px solid var(--accent);
  padding:11px 15px;border-radius:0 8px 8px 0;margin:0 0 18px;font-size:14.5px}
@media (max-width:640px){
  .bar{gap:9px}
  nav{order:3;flex-basis:100%}
  .hero{padding:30px 0 18px}
}
"""

JS = """
(function(){
  var root=document.documentElement;
  var stored=null;
  try{stored=localStorage.getItem('addpy-lang');}catch(e){}
  root.dataset.lang=(stored==='lt')?'lt':'en';   // English unless LT was chosen
  function sync(){
    document.querySelectorAll('.toggle button').forEach(function(b){
      b.setAttribute('aria-pressed', b.dataset.lang===root.dataset.lang);
    });
  }
  document.querySelectorAll('.toggle button').forEach(function(b){
    b.addEventListener('click',function(){
      root.dataset.lang=b.dataset.lang;
      try{localStorage.setItem('addpy-lang',b.dataset.lang);}catch(e){}
      sync();
    });
  });
  sync();

  var search=document.getElementById('api-search');
  if(search){
    search.addEventListener('input',function(){
      var q=search.value.trim().toLowerCase();
      document.querySelectorAll('.fn').forEach(function(f){
        var hit=!q||f.dataset.search.indexOf(q)>=0;
        f.style.display=hit?'':'none';
        if(q&&hit){f.open=true;}
        if(!q){f.open=false;}
      });
      document.querySelectorAll('.api-group').forEach(function(g){
        var any=g.querySelectorAll('.fn:not([style*="none"])').length;
        g.style.display=any?'':'none';
      });
    });
  }

  document.addEventListener('click',function(e){
    var b=e.target.closest('.copy');
    if(!b)return;
    var code=b.parentNode.querySelector('code');
    navigator.clipboard.writeText(code.textContent).then(function(){
      var old=b.innerHTML; b.innerHTML='&#10003;';
      setTimeout(function(){b.innerHTML=old;},1200);
    });
  });
})();
"""


def build():
    api = read_api()
    parts = []
    w = parts.append

    w("<!DOCTYPE html>")
    w('<html lang="en" data-lang="en"><head>')
    w('<meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>add.py %s &mdash; 3D models from code</title>" % content.VERSION)
    w('<meta name="description" content="add.py: build 3D models with '
      'nothing but Python code. No libraries, no modelling program.">')
    w("<style>%s</style>" % CSS)
    w("</head><body>")

    # ---- header
    w('<header><div class="bar">')
    w('<a class="brand" href="#top">add<span>.py</span></a>')
    w("<nav>")
    for anchor, key in (("start", "nav_start"), ("concepts", "nav_concepts"),
                        ("gallery", "nav_gallery"), ("cookbook", "nav_cookbook"),
                        ("reference", "nav_reference"), ("upgrade", "nav_upgrade"),
                        ("faq", "nav_faq")):
        w('<a href="#%s"><span class="only-en">%s</span>'
          '<span class="only-lt">%s</span></a>'
          % (anchor, content.UI[key]["en"], content.UI[key]["lt"]))
    w("</nav>")
    w('<div class="toggle"><button data-lang="en">EN</button>'
      '<button data-lang="lt">LT</button></div>')
    w("</div></header>")

    w('<main id="top">')

    # ---- hero
    w('<div class="hero">')
    w('<h1>add<span>.py</span></h1>')
    w('<p class="lead"><span class="only-en">%s</span>'
      '<span class="only-lt">%s</span></p>'
      % (content.UI["tagline"]["en"], content.UI["tagline"]["lt"]))
    w('<p class="lead" style="font-size:16px"><span class="only-en">'
      "One file. Only <code>math</code> and <code>random</code>. "
      "No modelling program, no mesh library, no install."
      '</span><span class="only-lt">'
      "Vienas failas. Tik <code>math</code> ir <code>random</code>. "
      "Jokios modeliavimo programos, jokios geometrijos bibliotekos, "
      "nieko diegti nereikia.</span></p>")
    w('<div class="badges">')
    for text in ("v%s" % content.VERSION, "MIT", "Python 3",
                 "%d functions" % sum(len(e) for _, e in api),
                 "0 dependencies"):
        w('<span class="badge">%s</span>' % text)
    w("</div></div>")

    # ---- narrative sections
    for anchor, texts in content.SECTIONS:
        if anchor == "cookbook":
            w(_gallery_section())
        w('<section id="%s">' % anchor)
        w('<div class="only-en">%s</div>' % markdown(texts["en"]))
        w('<div class="only-lt">%s</div>' % markdown(texts["lt"]))
        w("</section>")
        if anchor == "cookbook":
            w(_reference_section(api))

    w("</main>")

    w('<footer><div class="bar" style="padding-left:0;padding-right:0">'
      '<span class="only-en">%s</span><span class="only-lt">%s</span></div>'
      "</footer>" % (content.UI["footer"]["en"], content.UI["footer"]["lt"]))
    w("<script>%s</script>" % JS)
    w("</body></html>")

    page = "\n".join(parts)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(page)
    return page, api


def _gallery_section():
    out = ['<section id="gallery">',
           '<h2><span class="only-en">Gallery</span>'
           '<span class="only-lt">Galerija</span></h2>',
           '<p><span class="only-en">Every picture below was made by one '
           'script in <code>examples/</code>, and every script is meant to be '
           'read.</span><span class="only-lt">Kiekvienas paveikslėlis sukurtas '
           'viena programa iš <code>examples/</code> aplanko, ir kiekviena jų '
           'skirta skaityti.</span></p>',
           '<div class="gallery">']
    for image, script, cap_en, cap_lt in content.GALLERY:
        out.append(
            '<figure><img loading="lazy" src="images/%s" alt="%s">'
            '<figcaption><b>%s</b>'
            '<span class="only-en">%s</span>'
            '<span class="only-lt">%s</span></figcaption></figure>'
            % (image, html.escape(cap_en), html.escape(script),
               html.escape(cap_en), html.escape(cap_lt)))
    out.append("</div></section>")
    return "\n".join(out)


def _reference_section(api):
    out = ['<section id="reference">',
           '<h2><span class="only-en">Reference</span>'
           '<span class="only-lt">Funkcijos</span></h2>',
           '<p class="note only-lt">%s</p>' % content.UI["lang_note"]["lt"],
           '<div class="tools">'
           '<input type="search" id="api-search" placeholder="%s" '
           'aria-label="%s"></div>'
           % (content.UI["search"]["en"], content.UI["search"]["en"])]
    used = coverage.usage()
    for title, entries in api:
        out.append('<div class="api-group"><h3>%s</h3>' % html.escape(title))
        for e in entries:
            summary_en = (e["doc"].split("\n")[0] if e["doc"] else "")
            summary_lt = content.SHORT.get(e["name"], summary_en)
            body = docstring_html(e["doc"])
            scripts = used.get(e["name"], [])
            if scripts:
                links = ", ".join(
                    '<a href="%s/blob/main/examples/%s">%s</a>' % (content.REPO_URL, name, name[:-3])
                    for name in scripts[:6])
                if len(scripts) > 6:
                    links += ", &hellip;"
                body += ('<p class="used"><span class="only-en">Used in: </span>'
                         '<span class="only-lt">Naudojama: </span>%s</p>' % links)
            search_key = (e["name"] + " " + summary_en + " "
                          + summary_lt).lower()
            head = ('<span class="nm">%s</span>'
                    '<span class="sig">%s</span>'
                    '<span class="sum only-en">%s</span>'
                    '<span class="sum only-lt">%s</span>'
                    % (e["name"], html.escape(e["signature"]),
                       html.escape(summary_en), html.escape(summary_lt)))
            if body:
                out.append('<details class="fn" id="fn-%s" data-search="%s">'
                           '<summary>%s</summary><div class="body">%s</div>'
                           '</details>'
                           % (e["name"], html.escape(search_key, quote=True),
                              head, body))
            else:
                out.append('<div class="fn flat" id="fn-%s" data-search="%s">'
                           '<div class="head">%s</div></div>'
                           % (e["name"], html.escape(search_key, quote=True),
                              head))
        out.append("</div>")
    out.append("</section>")
    return "\n".join(out)


if __name__ == "__main__":
    page, api = build()
    total = sum(len(e) for _, e in api)
    missing = [e["name"] for _, entries in api for e in entries
               if e["name"] not in content.SHORT]
    print("docs/index.html written: %d KB, %d entries in %d groups"
          % (len(page) // 1024, total, len(api)))
    if missing:
        print("no Lithuanian one-liner for: %s" % ", ".join(sorted(missing)))
