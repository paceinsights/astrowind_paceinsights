"""Read-only local board: tasks serve. Reads the tasks/ files on every request."""

from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .core import Decision, Item, Move, created_at, sort_key

COLUMNS = ("doing", "blocked", "todo", "held", "done", "dropped")
LABELS = {"doing": "Doing", "blocked": "Blocked", "todo": "To do", "held": "Held", "done": "Done", "dropped": "Dropped"}

STYLE = """
:root { --bg:#f6f7f9; --card:#fff; --ink:#1d2330; --muted:#667085; --line:#e4e7ec; --accent:#3559e0;
  --doing:#3559e0; --blocked:#d92d20; --todo:#667085; --held:#b54708; --done:#079455; --dropped:#98a2b3; }
@media (prefers-color-scheme: dark) { :root { --bg:#14171f; --card:#1d2230; --ink:#e6e9ef; --muted:#98a2b3;
  --line:#2c3344; --accent:#7c97ff; } }
* { box-sizing:border-box; }
body { margin:0; font:14px/1.45 -apple-system, system-ui, sans-serif; background:var(--bg); color:var(--ink); }
header { display:flex; gap:16px; align-items:center; flex-wrap:wrap; padding:14px 20px; border-bottom:1px solid var(--line); }
header h1 { font-size:17px; margin:0 12px 0 0; }
nav a { color:var(--muted); text-decoration:none; margin-right:14px; }
nav a.on { color:var(--ink); font-weight:600; }
select { font:inherit; padding:4px 8px; border-radius:6px; border:1px solid var(--line); background:var(--card); color:var(--ink); }
main { padding:16px 20px; }
.board { display:grid; grid-template-columns:repeat(6, minmax(200px, 1fr)); gap:12px; overflow-x:auto; }
.col h2 { font-size:13px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:0 0 8px; }
.col h2 b { color:var(--ink); }
.card { background:var(--card); border:1px solid var(--line); border-left:4px solid var(--c); border-radius:8px;
  padding:9px 10px; margin-bottom:8px; }
.meta { display:flex; gap:6px; flex-wrap:wrap; font-size:12px; color:var(--muted); margin-bottom:3px; }
.tag { background:var(--bg); border:1px solid var(--line); border-radius:999px; padding:0 7px; }
.due { color:var(--blocked); font-weight:600; }
.note { color:var(--muted); font-size:12.5px; margin-top:4px; }
.link { font-size:12px; word-break:break-all; color:var(--accent); }
table { border-collapse:collapse; width:100%; background:var(--card); }
td, th { text-align:left; vertical-align:top; padding:8px 10px; border-bottom:1px solid var(--line); }
th { font-size:12px; color:var(--muted); text-transform:uppercase; }
.old { opacity:.5; }
pre { white-space:pre-wrap; background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px; }
ul.files a { color:var(--accent); }
"""


def _e(text: str) -> str:
    return html.escape(text, quote=True)


def _page(store, title: str, active: str, body: str, area: str = "") -> bytes:
    tabs = [("/", "Board"), ("/decisions", "Decisions")]
    if store.has_health:
        tabs.append(("/health", "Platform health"))
    nav = "".join(f'<a href="{href}" class="{"on" if href == active else ""}">{label}</a>' for href, label in tabs)
    picker = ""
    if active == "/":
        options = '<option value="">All areas</option>' + "".join(
            f'<option value="{a}" {"selected" if a == area else ""}>{a}</option>' for a in store.settings.areas
        )
        picker = f"<select onchange=\"location.search=this.value?'?area='+this.value:''\">{options}</select>"
    return (
        f"<!doctype html><html lang=en><head><meta charset=utf-8>"
        f'<meta name=viewport content="width=device-width,initial-scale=1"><title>{_e(title)}</title>'
        f"<style>{STYLE}</style></head><body><header><h1>{_e(store.settings.name)} jobs</h1><nav>{nav}</nav>{picker}</header>"
        f"<main>{body}</main></body></html>"
    ).encode()


def _card(item: Item) -> str:
    due = f'<span class="due">due {_e(item.due)}</span>' if item.due else ""
    link = f'<div class="link">{_e(item.link)}</div>' if item.link else ""
    note = f'<div class="note">{_e(item.note)}</div>' if item.note else ""
    return (
        f'<div class="card" style="--c:var(--{item.state})"><div class="meta"><b>{_e(item.id)}</b>'
        f'<span class="tag">{_e(item.area)}</span><span>p{item.priority}</span>{due}</div>'
        f"<div>{_e(item.title)}</div>{note}{link}</div>"
    )


def board(items: list[Item], moves: list[Move], area: str) -> str:
    shown = [i for i in items if not area or i.area == area]
    created = created_at(moves)
    cols = []
    for state in COLUMNS:
        group = sorted((i for i in shown if i.state == state), key=lambda i: sort_key(i, created))
        if state == "done":
            group.sort(key=lambda i: i.updated, reverse=True)
        cards = "".join(_card(i) for i in group)
        cols.append(f'<section class="col"><h2>{LABELS[state]} <b>{len(group)}</b></h2>{cards}</section>')
    return f'<div class="board">{"".join(cols)}</div>'


def decisions_table(decisions: list[Decision]) -> str:
    superseded = {d.supersedes for d in decisions if d.supersedes}
    rows = "".join(
        f'<tr class="{"old" if d.id in superseded else ""}"><td><b>{_e(d.id)}</b></td><td>{_e(d.date)}</td>'
        f"<td>{_e(d.area)}</td><td>{_e(d.decision)}</td><td>{_e(d.why)}</td><td>{_e(d.evidence)}</td>"
        f"<td>{_e(d.supersedes)}</td></tr>"
        for d in sorted(decisions, key=lambda d: (d.date, d.id), reverse=True)
    )
    return (
        "<table><tr><th>Id</th><th>Date</th><th>Area</th><th>Decision</th><th>Why</th>"
        f"<th>Evidence</th><th>Supersedes</th></tr>{rows}</table>"
    )


def health(root: Path, name: str) -> str:
    folder = root / "platform-health"
    files = sorted((p for p in folder.glob("*.md") if p.name != "README.md"), reverse=True)
    if not files:
        return "<p>No reports yet.</p>"
    chosen = next((p for p in files if p.name == name), files[0])
    links = "".join(f'<li><a href="/health?f={_e(p.name)}">{_e(p.stem)}</a></li>' for p in files)
    return (
        f'<div style="display:grid;grid-template-columns:160px 1fr;gap:16px"><ul class="files">{links}</ul>'
        f"<div><h2>{_e(chosen.stem)}</h2><pre>{_e(chosen.read_text(encoding='utf-8'))}</pre></div></div>"
    )


def serve(store, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            url = urlparse(self.path)
            query = parse_qs(url.query)
            items, moves, decisions = store.load()
            if url.path == "/":
                area = query.get("area", [""])[0]
                body = _page(store, f"{store.settings.name} jobs", "/", board(items, moves, area), area)
            elif url.path == "/decisions":
                body = _page(store, "Decisions", "/decisions", decisions_table(decisions))
            elif url.path == "/health" and store.has_health:
                body = _page(store, "Platform health", "/health", health(store.root, unquote(query.get("f", [""])[0])))
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"{store.settings.name} board at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
