#!/usr/bin/env python3
"""artifact_create — render a consistently-styled, self-contained HTML report.

The house template (CSS + theme toggle + mandatory copy-page button) lives HERE,
as the single source of truth, so every artifact looks the same and ships the
same affordances. It writes to a neutral artifacts root served locally by
artifact_serve.py.

Usage:
  artifact_create.py --title T --slug S [--summary X] [--tag "Field Memo"]
                     (--html-file F.html | --body-file F.md | markdown on stdin)
                     [--root ~/artifacts/public] [--base-url URL]

--html-file: a fully-authored page. Placed as-is; the copy-page button is
             injected if the author didn't already include one.
--body-file / stdin: markdown, wrapped in the house template.
"""
import argparse
import datetime
import errno
import html
import json
import os
import re
import stat
import sys
from urllib.parse import urlsplit

from artifact_fs import (
    atomic_write_text,
    list_names_checked,
    normalized_absolute,
    open_absolute_regular,
    open_child_directory,
    open_directory,
    open_regular_at,
)

HOUSE_CSS = r"""
img{cursor:zoom-in}

  :root{--bg:#f5f0e4;--panel:#fbf7ed;--ink:#241f19;--muted:#6b6053;--line:#e2d9c6;--red:#b4392a;--teal:#2c7a68;--gold:#bd8f2e;--shadow:0 1px 0 rgba(0,0,0,.04),0 12px 30px -22px rgba(40,30,20,.5);--col:52rem;}
  html[data-theme="dark"]{--bg:#11141a;--panel:#171b22;--ink:#e9e3d5;--muted:#9aa0ab;--line:#282e38;--red:#e3674f;--teal:#54bba4;--gold:#d8b25a;--shadow:0 1px 0 rgba(0,0,0,.3),0 16px 40px -26px rgba(0,0,0,.9);}
  @media (prefers-color-scheme:dark){html[data-theme="auto"]{--bg:#11141a;--panel:#171b22;--ink:#e9e3d5;--muted:#9aa0ab;--line:#282e38;--red:#e3674f;--teal:#54bba4;--gold:#d8b25a;--shadow:0 1px 0 rgba(0,0,0,.3),0 16px 40px -26px rgba(0,0,0,.9);}}
  *{box-sizing:border-box} html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;padding:0 1.1rem 5rem;background-image:radial-gradient(circle at 12% -5%,rgba(189,143,46,.07),transparent 36%),radial-gradient(circle at 92% 4%,rgba(44,122,104,.07),transparent 34%);}
  .wrap{max-width:var(--col);margin:0 auto}
  .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
  a{color:var(--red);text-underline-offset:2px;overflow-wrap:anywhere}
  h1,h2,h3{line-height:1.2;font-weight:680}
  h1{font-family:Georgia,"Times New Roman",serif;font-weight:600;font-size:clamp(1.85rem,5.2vw,2.6rem);letter-spacing:-.01em;margin:.2em 0 .15em}
  h2{font-size:1.32rem;margin:2.3em 0 .3em} h2 .k{font:600 .72rem/1 ui-monospace,monospace;color:var(--red);vertical-align:.5em;margin-right:.55em}
  h3{font-size:1.04rem;margin:1.3em 0 .25em}
  p{margin:.55em 0} small{color:var(--muted)}
  header.bar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);margin:0 -1.1rem 1.6rem;padding:.55rem 1.1rem}
  .bar .row{max-width:var(--col);margin:0 auto;display:flex;align-items:center;gap:.6rem}
  .tag{font:600 .68rem/1 ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
  .dot{width:.5rem;height:.5rem;border-radius:50%;background:var(--teal);animation:pulse 2.6s infinite}
  @keyframes pulse{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--teal) 60%,transparent)}70%{box-shadow:0 0 0 7px transparent}100%{box-shadow:0 0 0 0 transparent}}
  .spacer{flex:1}
  .toggle{cursor:pointer;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:600 .72rem/1 ui-monospace,monospace;padding:.42rem .7rem;border-radius:2em;display:inline-flex;gap:.4rem;align-items:center}
  .toggle:hover{border-color:var(--red)}
  .label{font:600 .72rem/1 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--red)}
  .lede{font-size:1.12rem;color:var(--muted);margin:.4em 0 1em}
  .pill{font:600 .68rem/1.4 ui-monospace,monospace;border:1px solid var(--line);border-radius:2em;padding:.28em .7em;color:var(--muted);background:var(--panel)}
  .call{border:1px solid var(--line);border-left:4px solid var(--teal);background:color-mix(in srgb,var(--teal) 7%,var(--panel));border-radius:.6rem;padding:.8rem 1.05rem;margin:1.1rem 0}
  .call.red{border-left-color:var(--red);background:color-mix(in srgb,var(--red) 7%,var(--panel))}
  .call.gold{border-left-color:var(--gold);background:color-mix(in srgb,var(--gold) 8%,var(--panel))}
  .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1rem 0;border:1px solid var(--line);border-radius:.6rem}
  table{border-collapse:collapse;width:100%;font-size:.88rem;background:var(--panel)}
  th,td{text-align:left;padding:.55rem .65rem;border-bottom:1px solid var(--line);vertical-align:top}
  th{font:600 .66rem/1.3 ui-monospace,monospace;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);background:color-mix(in srgb,var(--panel) 70%,var(--bg))}
  tr:last-child td{border-bottom:0}
  code{font-family:ui-monospace,monospace;font-size:.85em;background:color-mix(in srgb,var(--ink) 8%,transparent);padding:.1em .35em;border-radius:.3em;overflow-wrap:anywhere}
  pre{background:var(--panel);border:1px solid var(--line);border-radius:.6rem;padding:.9rem;overflow-x:auto;font:600 .78rem/1.5 ui-monospace,monospace;color:var(--ink)}
  blockquote{border-left:3px solid var(--gold);margin:.8em 0;padding:.2em 0 .2em 1rem;color:var(--muted)}
  footer{margin-top:2.6rem;border-top:1px solid var(--line);padding-top:1rem;color:var(--muted);font-size:.85rem}
  @media (prefers-reduced-motion:reduce){.dot{animation:none} html{scroll-behavior:auto}}
"""

# Theme toggle + the MANDATORY copy-page button. Copies the whole document.
HOUSE_JS = r"""
(function(){
  var root=document.documentElement,k="hk-artifact-theme";
  var order=["auto","light","dark"],icons={auto:"◐",light:"☀",dark:"☾"},names={auto:"System",light:"Light",dark:"Dark"};
  var saved=null;try{saved=localStorage.getItem(k)}catch(e){}
  var cur=order.indexOf(saved)>=0?saved:"auto";
  function apply(){root.setAttribute("data-theme",cur);var i=document.getElementById("tgicon"),t=document.getElementById("tgtxt");if(i)i.textContent=icons[cur];if(t)t.textContent=names[cur];}
  apply();
  var tg=document.getElementById("tg");if(tg)tg.addEventListener("click",function(){cur=order[(order.indexOf(cur)+1)%order.length];try{localStorage.setItem(k,cur)}catch(e){}apply();});
  var cp=document.getElementById("cp"),cpt=document.getElementById("cptxt");
  // Lightbox: click any content image for full size.
  document.addEventListener("click",function(e){
    var t=e.target;
    if(t.tagName==="IMG"&&!t.closest("a")&&!t.closest("#hk-lb")){
      var o=document.createElement("div");o.id="hk-lb";
      o.style.cssText="position:fixed;inset:0;background:rgba(0,0,0,.85);display:flex;align-items:center;justify-content:center;z-index:999;cursor:zoom-out;padding:2vh 2vw";
      var im=document.createElement("img");im.src=t.src;
      im.style.cssText="max-width:96vw;max-height:96vh;width:auto;height:auto;box-shadow:0 8px 40px rgba(0,0,0,.6)";
      o.appendChild(im);o.addEventListener("click",function(){o.remove()});
      document.addEventListener("keydown",function esc(ev){if(ev.key==="Escape"){o.remove();document.removeEventListener("keydown",esc)}});
      document.body.appendChild(o);
    }
  });
  if(cp)cp.addEventListener("click",function(){var doc="<!doctype html>\n"+document.documentElement.outerHTML;
    function ok(){if(cpt){cpt.textContent="Copied ✓";setTimeout(function(){cpt.textContent="Copy page"},1600);}}
    function fallback(){var ta=document.createElement("textarea");ta.value=doc;ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.focus();ta.select();try{document.execCommand("copy");ok()}catch(e){if(cpt)cpt.textContent="Copy failed"}document.body.removeChild(ta);}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(doc).then(ok,fallback)}else{fallback()}});
})();
"""

HEADER = ('<header class="bar"><div class="row">'
          '<span class="dot" aria-hidden="true"></span>'
          '<span class="tag">{tag}</span><span class="spacer"></span>'
          '<button class="toggle" id="cp" aria-label="Copy page HTML"><span id="cpicon">⧉</span><span id="cptxt">Copy page</span></button>'
          '<button class="toggle" id="tg" aria-label="Toggle theme"><span id="tgicon">◐</span><span id="tgtxt">System</span></button>'
          '</div></header>')

COPY_BTN_SNIPPET = ('<button class="toggle" id="cp" aria-label="Copy page HTML">'
                    '<span id="cpicon">⧉</span><span id="cptxt">Copy page</span></button>')

COPY_HANDLER_SNIPPET = (
    '<script data-hk-artifact-copy>(function(){var cp=document.getElementById("cp"),cpt=document.getElementById("cptxt");'
    'if(!cp)return;cp.addEventListener("click",function(){var d="<!doctype html>\\n"+document.documentElement.outerHTML;'
    'function ok(){if(cpt){cpt.textContent="Copied \\u2713";setTimeout(function(){cpt.textContent="Copy page"},1600);}}'
    'function fallback(){var ta=document.createElement("textarea");ta.value=d;ta.style.position="fixed";ta.style.opacity="0";'
    'document.body.appendChild(ta);ta.focus();ta.select();try{document.execCommand("copy");ok()}catch(e){if(cpt)cpt.textContent="Copy failed"}'
    'document.body.removeChild(ta);}'
    'if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(d).then(ok,fallback)}else{fallback()}});})();</script>'
)


def md_to_html(md: str) -> str:
    """Small dependency-free markdown renderer: headings, bold/italic/code,
    fenced code, blockquotes, ul/ol, tables (pipe), paragraphs."""
    out, i, lines = [], 0, md.split("\n")
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
        return s
    n = len(lines)
    while i < n:
        ln = lines[i]
        if ln.strip().startswith("```"):
            i += 1; buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i], quote=False)); i += 1
            i += 1; out.append("<pre>" + "\n".join(buf) + "</pre>"); continue
        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if ln.strip().startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(inline(lines[i].strip()[1:].strip())); i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>"); continue
        if "|" in ln and i + 1 < n and re.match(r"^[\s|:-]+$", lines[i+1]):
            hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2; rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = ["<div class='scroll'><table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in hdr] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>"); out.append("".join(t)); continue
        if re.match(r"^\s*[-*]\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>"); continue
        if ln.strip() == "":
            i += 1; continue
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,3}\s|```|>|\s*[-*]\s|\s*\d+\.\s)", lines[i]):
            buf.append(inline(lines[i])); i += 1
        out.append("<p>" + " ".join(buf) + "</p>")
    return "\n".join(out)


def wrap(title, tag, summary, body_html):
    lede = f'<p class="lede">{html.escape(summary)}</p>' if summary else ""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{HOUSE_CSS}</style>
</head>
<body>
{HEADER.format(tag=html.escape(tag))}
<div class="wrap">
<h1>{html.escape(title)}</h1>
{lede}
{body_html}
<footer><p class="mono">artifact · {stamp}</p></footer>
</div>
<script>{HOUSE_JS}</script>
</body>
</html>"""


def ensure_copy_button(doc: str) -> str:
    """Inject the copy-page button + its JS into an authored full HTML doc if absent."""
    if 'id="cp"' not in doc:
        # add button before the theme toggle if present, else after <body>
        if 'id="tg"' in doc:
            doc = doc.replace('<button class="toggle" id="tg"', COPY_BTN_SNIPPET + '\n  <button class="toggle" id="tg"', 1)
        else:
            doc = re.sub(r"(<body[^>]*>)", r"\1\n" + HEADER.format(tag="Artifact"), doc, count=1)
    if 'id="cp"' in doc and "data-hk-artifact-copy" not in doc and "</body>" in doc:
        doc = doc.replace("</body>", COPY_HANDLER_SNIPPET + "\n</body>", 1)
    # The shelf may inject its own footer at serve time, so authored pages
    # carry no deployment-specific home affordance.
    return doc


INDEX_SLUG = "index"


def prepare_root(path):
    root = normalized_absolute(path)
    return root, open_directory(root, create=True)


def open_artifact_dir(root_fd, slug):
    """Create and return an artifact directory anchored below the root fd."""
    artifacts_fd = None
    try:
        artifacts_fd = open_child_directory(root_fd, "a", create=True)
        return open_child_directory(artifacts_fd, slug, create=True)
    finally:
        if artifacts_fd is not None:
            os.close(artifacts_fd)


def read_text(directory_fd, name, errors="strict"):
    fd = open_regular_at(directory_fd, name)
    with os.fdopen(fd, encoding="utf-8", errors=errors) as source:
        return source.read()


def read_input(path, label):
    """Read one regular input through held, no-follow parent descriptors."""
    try:
        fd = open_absolute_regular(path)
    except ValueError as err:
        raise ValueError(f"{label}: {err}") from err
    with os.fdopen(fd, encoding="utf-8") as input_file:
        return input_file.read()


def normalize_local_base_url(value):
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as err:
        raise ValueError(f"invalid local base URL: {value}") from err
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("127.0.0.1", "localhost")
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise ValueError(
            "--base-url must be an HTTP loopback origin such as "
            "http://127.0.0.1:8789"
        )
    authority = parsed.hostname
    if port is not None:
        authority = f"{authority}:{port}"
    return f"http://{authority}"


def load_registry(root_fd):
    artifacts_fd = index_fd = None
    try:
        artifacts_fd = open_child_directory(root_fd, "a")
        index_fd = open_child_directory(artifacts_fd, INDEX_SLUG)
        data = json.loads(read_text(index_fd, "index.json"))
        return {e["slug"]: e for e in data.get("artifacts", [])}
    except OSError as err:
        if err.errno in (errno.ENOENT, errno.ENOTDIR):
            return {}
        raise
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return {}
    finally:
        for directory in (index_fd, artifacts_fd):
            if directory is not None:
                os.close(directory)


def pin_starred(entries):
    """Starred first, newest-first within each group (stable two-pass sort:
    Timsort preserves the updated-time order the starred pass groups by)."""
    entries = sorted(entries, key=lambda x: x.get("updated", ""), reverse=True)
    return sorted(entries, key=lambda x: x.get("starred", False), reverse=True)


def render_index_html(entries, base_url):
    entries = pin_starred(entries)
    rows = []
    for e in entries:
        star = "★ " if e.get("starred") else ""
        rows.append(
            f'<tr><td>{star}<a href="{html.escape(base_url)}/a/{html.escape(e["slug"])}/">'
            f'{html.escape(e.get("title") or e["slug"])}</a></td>'
            f'<td>{html.escape(e.get("tag", ""))}</td>'
            f'<td>{html.escape(e.get("summary", ""))}</td>'
            f'<td class="mono">{html.escape((e.get("updated") or "")[:16])}</td></tr>'
        )
    body = (
        "<h2>Shelf index</h2>"
        "<p>Every locally rendered artifact, newest first. "
        "Machine-readable twin: <a href=\"index.json\">index.json</a>.</p>"
        "<div class='scroll'><table><thead><tr><th>Artifact</th><th>Tag</th><th>Summary</th>"
        "<th>Updated (UTC)</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )
    return wrap("Shelf Index", "Registry", f"{len(entries)} artifacts on the shelf.", body)


def update_index(root_fd, base_url, entry):
    """Upsert one registry entry and rewrite the local index files.

    The registry is itself an artifact (slug "index"): the shelf serves static
    files only, so the index rides the exact same local-file contract as every
    page. Best-effort — an index failure must never fail the artifact render.
    """
    try:
        reg = load_registry(root_fd)
        prev = reg.get(entry["slug"], {})
        entry["created"] = prev.get("created") or entry["updated"]
        reg[entry["slug"]] = {**prev, **entry}
        entries = [e for s, e in reg.items() if s != INDEX_SLUG]
        entries = pin_starred(entries)
        idx_fd = open_artifact_dir(root_fd, INDEX_SLUG)
        try:
            payload = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "count": len(entries), "artifacts": entries}
            atomic_write_text(idx_fd, "index.json", json.dumps(payload, indent=1))
            doc = render_index_html(entries, base_url.rstrip("/"))
            atomic_write_text(idx_fd, "index.html", doc)
            return len(entries)
        finally:
            os.close(idx_fd)
    except Exception as err:  # noqa: BLE001 — index is best-effort by contract
        print(f"index update skipped ({err})", file=sys.stderr)
        return None


def reindex(root_fd, base_url):
    """Backfill the registry from the local mirror (title from each page)."""
    try:
        reg = load_registry(root_fd)
    except OSError:
        # Reindex can reconstruct metadata from safely opened pages even when
        # a prior registry leaf is unsafe to read.
        reg = {}
    a_fd = open_child_directory(root_fd, "a", create=True)
    try:
        for slug in sorted(list_names_checked(a_fd)):
            if slug == INDEX_SLUG or slug in reg:
                continue
            slug_fd = None
            page_fd = None
            try:
                slug_fd = open_child_directory(a_fd, slug)
                page_fd = open_regular_at(slug_fd, "index.html")
                page_stat = os.fstat(page_fd)
                if not stat.S_ISREG(page_stat.st_mode):
                    continue
                with os.fdopen(page_fd, encoding="utf-8", errors="ignore") as page_file:
                    page_fd = None
                    head = page_file.read(4000)
            except (OSError, ValueError):
                continue
            finally:
                if page_fd is not None:
                    os.close(page_fd)
                if slug_fd is not None:
                    os.close(slug_fd)
            m = re.search(r"<title>(.*?)</title>", head, re.S)
            mtime = datetime.datetime.fromtimestamp(page_stat.st_mtime, datetime.timezone.utc)
            reg[slug] = {"slug": slug,
                         "title": (m.group(1).strip() if m else slug),
                         "tag": "", "summary": "",
                         "created": mtime.isoformat(timespec="seconds"),
                         "updated": mtime.isoformat(timespec="seconds")}
        entries = [e for s, e in reg.items() if s != INDEX_SLUG]
        entries = pin_starred(entries)
        idx_fd = open_artifact_dir(root_fd, INDEX_SLUG)
        try:
            payload = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "count": len(entries), "artifacts": entries}
            atomic_write_text(idx_fd, "index.json", json.dumps(payload, indent=1))
            doc = render_index_html(entries, base_url.rstrip("/"))
            atomic_write_text(idx_fd, "index.html", doc)
            return len(entries)
        finally:
            os.close(idx_fd)
    finally:
        os.close(a_fd)


def render_command(a, ap, root_fd):
    """Run one render/reindex transaction against a single held root FD."""
    if a.reindex:
        n = reindex(root_fd, a.base_url)
        print(json.dumps({"reindexed": n,
                          "url": f"{a.base_url.rstrip('/')}/a/{INDEX_SLUG}/"}, indent=2))
        return
    if not a.title or not a.slug:
        ap.error("--title and --slug are required (unless --reindex)")

    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", a.slug).strip("-").lower()
    if not slug:
        ap.error("--slug must contain at least one letter or digit")
    if slug == INDEX_SLUG:
        ap.error(f"--slug {INDEX_SLUG!r} is reserved for the local registry")
    if a.html_file:
        try:
            doc = read_input(a.html_file, "HTML input")
        except (OSError, ValueError) as err:
            ap.error(str(err))
        if "<html" in doc.lower():
            doc = ensure_copy_button(doc)
        else:
            doc = wrap(a.title, a.tag, a.summary, doc)
    else:
        if a.body_file:
            try:
                md = read_input(a.body_file, "markdown input")
            except (OSError, ValueError) as err:
                ap.error(str(err))
        else:
            md = sys.stdin.read()
        doc = wrap(a.title, a.tag, a.summary, md_to_html(md))

    try:
        dest_dir = open_artifact_dir(root_fd, slug)
    except (OSError, ValueError) as err:
        ap.error(str(err))
    dest = os.path.join(a.root, "a", slug, "index.html")
    try:
        atomic_write_text(dest_dir, "index.html", doc)
    finally:
        os.close(dest_dir)
    url = f"{a.base_url.rstrip('/')}/a/{slug}/"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    indexed = update_index(root_fd, a.base_url,
                           {"slug": slug, "title": a.title, "tag": a.tag,
                            "summary": a.summary, "updated": now_iso})
    print(json.dumps({"slug": slug, "path": dest, "url": url, "bytes": len(doc),
                      "indexed": indexed, "local_only": True}, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reindex", action="store_true",
                    help="backfill the shelf registry from the local mirror and exit")
    ap.add_argument("--title")
    ap.add_argument("--slug")
    ap.add_argument("--summary", default="")
    ap.add_argument("--tag", default="Artifact")
    ap.add_argument("--html-file")
    ap.add_argument("--body-file")
    ap.add_argument("--root", default=os.path.expanduser("~/artifacts/public"))
    ap.add_argument("--base-url", default="http://127.0.0.1:8789",
                    help="local serving URL used in generated index links")
    a = ap.parse_args()

    root_fd = None
    try:
        a.base_url = normalize_local_base_url(a.base_url)
        a.root, root_fd = prepare_root(a.root)
        render_command(a, ap, root_fd)
    except ValueError as err:
        ap.error(str(err))
    finally:
        if root_fd is not None:
            os.close(root_fd)


if __name__ == "__main__":
    main()
