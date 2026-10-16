"""Pure tracker logic: the item model, the state machine, validation and the STATUS.md view.

No file IO here. cli.py reads tracker.ini and the TSV files and calls these functions.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, fields, replace

STATES = ("todo", "doing", "blocked", "held", "done", "dropped")

# Every legal move. Anything not listed is refused.
TRANSITIONS: dict[str, frozenset[str]] = {
    "todo": frozenset({"doing", "blocked", "held", "done", "dropped"}),
    "doing": frozenset({"todo", "blocked", "held", "done", "dropped"}),
    "blocked": frozenset({"todo", "doing", "held", "dropped"}),
    "held": frozenset({"todo", "dropped"}),
    "done": frozenset({"todo"}),
    "dropped": frozenset({"todo"}),
}

# Moving into these states needs a note saying why (or, for done, the evidence).
NOTE_REQUIRED = frozenset({"blocked", "held", "done", "dropped"})

AREA = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class Settings:
    """One project's tracker.ini: its name and the areas its jobs and decisions can belong to."""

    name: str
    areas: tuple[str, ...]


# New ids are the day plus three random characters (T-1016-k3x), so two branches adding jobs at the same time
# can't pick the same id. Ids from before that (T-001, D-001) stay valid.
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
ITEM_ID = re.compile(r"^T-(\d{3,}|\d{4}-[a-z2-9]{3})$")
DECISION_ID = re.compile(r"^D-(\d{3,}|\d{4}-[a-z2-9]{3})$")
LEGACY_DECISION_ID = re.compile(r"^D-\d{3,}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class TrackerError(ValueError):
    """A request the tracker refuses, or a file that breaks the rules."""


@dataclass(frozen=True)
class Item:
    id: str
    state: str
    priority: int
    area: str
    title: str
    due: str = ""
    link: str = ""
    note: str = ""
    updated: str = ""


@dataclass(frozen=True)
class Move:
    ts: str
    id: str
    from_state: str
    to_state: str
    note: str = ""


@dataclass(frozen=True)
class Decision:
    id: str
    date: str
    area: str
    decision: str
    why: str
    evidence: str
    supersedes: str = ""


ITEM_COLUMNS = tuple(f.name for f in fields(Item))
MOVE_COLUMNS = ("ts", "id", "from", "to", "note")
DECISION_COLUMNS = tuple(f.name for f in fields(Decision))


def clean_cell(value: str, column: str) -> str:
    if "\t" in value or "\n" in value or "\r" in value:
        raise TrackerError(f"{column} cannot contain tabs or line breaks")
    return value.strip()


def _check_area(area: str, areas: tuple[str, ...]) -> None:
    if area not in areas:
        raise TrackerError(f"unknown area {area!r}. Areas: {', '.join(areas)}. To add one, edit tasks/tracker.ini")


def _check_due(due: str) -> None:
    if due and not DATE.match(due):
        raise TrackerError(f"due must be YYYY-MM-DD, got {due!r}")


def new_id(existing: list[str], prefix: str, today: str) -> str:
    taken = set(existing)
    while True:
        candidate = f"{prefix}-{today[5:7]}{today[8:10]}-" + "".join(secrets.choice(ID_CHARS) for _ in range(3))
        if candidate not in taken:
            return candidate


def add_item(
    items: list[Item],
    *,
    areas: tuple[str, ...],
    area: str,
    title: str,
    priority: int,
    today: str,
    now: str,
    state: str = "todo",
    due: str = "",
    link: str = "",
    note: str = "",
) -> tuple[Item, Move]:
    _check_area(area, areas)
    _check_due(due)
    if state not in STATES:
        raise TrackerError(f"unknown state {state!r}")
    if state in NOTE_REQUIRED and not note:
        raise TrackerError(f"a new item in state {state!r} needs --note")
    if priority < 1:
        raise TrackerError("priority must be 1 or more (1 is most urgent)")
    item = Item(
        id=new_id([i.id for i in items], "T", today),
        state=state,
        priority=priority,
        area=area,
        title=clean_cell(title, "title"),
        due=due,
        link=clean_cell(link, "link"),
        note=clean_cell(note, "note"),
        updated=now,
    )
    if not item.title:
        raise TrackerError("title cannot be empty")
    return item, Move(ts=now, id=item.id, from_state="", to_state=state, note=item.note)


def move_item(item: Item, to_state: str, *, note: str, today: str, now: str) -> tuple[Item, Move]:
    if to_state not in STATES:
        raise TrackerError(f"unknown state {to_state!r}. States: {', '.join(STATES)}")
    if to_state == item.state:
        raise TrackerError(f"{item.id} is already {to_state}")
    if to_state not in TRANSITIONS[item.state]:
        allowed = ", ".join(sorted(TRANSITIONS[item.state]))
        raise TrackerError(f"{item.id} cannot go from {item.state} to {to_state}. From {item.state}: {allowed}")
    note = clean_cell(note, "note")
    if to_state in NOTE_REQUIRED and not note:
        reason = "the evidence (PR, release, commit)" if to_state == "done" else "why"
        raise TrackerError(f"moving {item.id} to {to_state} needs --note with {reason}")
    moved = replace(item, state=to_state, note=note, updated=now)
    return moved, Move(ts=now, id=item.id, from_state=item.state, to_state=to_state, note=note)


def edit_item(item: Item, *, areas: tuple[str, ...], now: str, **changes: object) -> Item:
    """Change anything except the state. State changes go through move_item."""
    if "state" in changes:
        raise TrackerError("use move to change state")
    if "area" in changes:
        _check_area(str(changes["area"]), areas)
    if "due" in changes:
        _check_due(str(changes["due"]))
    for key in ("title", "link", "note", "due"):
        if key in changes:
            changes[key] = clean_cell(str(changes[key]), key)
    if "priority" in changes and int(changes["priority"]) < 1:
        raise TrackerError("priority must be 1 or more")
    return replace(item, updated=now, **changes)


def add_decision(
    decisions: list[Decision],
    *,
    areas: tuple[str, ...],
    area: str,
    decision: str,
    why: str,
    evidence: str,
    date: str,
    today: str,
    supersedes: str = "",
) -> Decision:
    _check_area(area, areas)
    if supersedes and supersedes not in {d.id for d in decisions}:
        raise TrackerError(f"supersedes {supersedes!r}, which does not exist")
    new = Decision(
        id=new_id([d.id for d in decisions], "D", today),
        date=date,
        area=area,
        decision=clean_cell(decision, "decision"),
        why=clean_cell(why, "why"),
        evidence=clean_cell(evidence, "evidence"),
        supersedes=supersedes,
    )
    if not (new.decision and new.why and new.evidence):
        raise TrackerError("a decision needs the decision, why and evidence")
    return new


def settle(
    items: list[Item], moves: list[Move], decisions: list[Decision]
) -> tuple[list[Item], list[Move], list[Decision], bool]:
    """Tidy the tables after a git merge that kept both branches' lines (tasks/.gitattributes, merge=union).

    A job that appears more than once keeps its newest version; two different versions changed at the same moment
    stay, so validate reports the duplicate. Repeated lines go, and history is put back in time order. Returns the
    tidied tables and whether anything changed.
    """
    newest: dict[str, list[Item]] = {}
    for item in items:
        kept = newest.setdefault(item.id, [])
        if item in kept:
            continue
        if kept and item.updated != kept[0].updated:
            if item.updated > kept[0].updated:
                kept[:] = [item]
            continue
        kept.append(item)
    order = list(dict.fromkeys(i.id for i in items))
    settled_items = [i for item_id in order for i in newest[item_id]]
    settled_moves = sorted(dict.fromkeys(moves), key=lambda m: m.ts)
    settled_decisions = list(dict.fromkeys(decisions))
    changed = (settled_items, settled_moves, settled_decisions) != (items, moves, decisions)
    return settled_items, settled_moves, settled_decisions, changed


def validate(items: list[Item], moves: list[Move], decisions: list[Decision], areas: tuple[str, ...]) -> list[str]:
    """Every rule the files must keep. Returns problems; empty means healthy."""
    problems: list[str] = []
    seen: set[str] = set()
    for item in items:
        where = f"items.tsv {item.id or '?'}"
        if not ITEM_ID.match(item.id):
            problems.append(f"{where}: id must look like T-1016-k3x (or T-001 from before)")
        if item.id in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(item.id)
        if item.state not in STATES:
            problems.append(f"{where}: unknown state {item.state!r}")
        if item.area not in areas:
            problems.append(f"{where}: unknown area {item.area!r}")
        if item.priority < 1:
            problems.append(f"{where}: priority must be 1 or more")
        if not item.title:
            problems.append(f"{where}: empty title")
        if item.due and not DATE.match(item.due):
            problems.append(f"{where}: due must be YYYY-MM-DD")
        if not (DATE.match(item.updated) or TIMESTAMP.match(item.updated)):
            problems.append(f"{where}: updated must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ")
        if item.state in NOTE_REQUIRED and not item.note:
            problems.append(f"{where}: state {item.state} needs a note")

    # history.tsv is a chain per item: each move starts where the last one ended. Two branches that moved the same
    # job differently break the chain here.
    last: dict[str, str] = {}
    for n, move in enumerate(moves, start=2):
        where = f"history.tsv line {n}"
        if not TIMESTAMP.match(move.ts):
            problems.append(f"{where}: ts must be YYYY-MM-DDTHH:MM:SSZ")
        expected_from = last.get(move.id, "")
        if move.from_state != expected_from:
            problems.append(
                f"{where}: {move.id} moves from {move.from_state or '(new)'}, but its last state was {expected_from or '(none)'}"
            )
        elif move.from_state and move.to_state not in TRANSITIONS.get(move.from_state, frozenset()):
            problems.append(f"{where}: {move.id} {move.from_state} to {move.to_state} is not a legal move")
        last[move.id] = move.to_state
    for item in items:
        if last.get(item.id) != item.state:
            problems.append(
                f"items.tsv {item.id}: state is {item.state} but history.tsv ends at {last.get(item.id, '(no history)')}"
            )
    for orphan in sorted(set(last) - seen):
        problems.append(f"history.tsv: {orphan} has history but no row in items.tsv")

    # decisions.tsv is append-only. The old numbered ids run D-001, D-002 ... with no gaps, so a removed one shows.
    legacy = [d for d in decisions if LEGACY_DECISION_ID.match(d.id)]
    for n, decision in enumerate(legacy, start=1):
        if decision.id != f"D-{n:03d}":
            problems.append(f"decisions.tsv {decision.id}: expected D-{n:03d} (rows are never removed or reordered)")
    decision_ids = [d.id for d in decisions]
    for decision in decisions:
        where = f"decisions.tsv {decision.id or '?'}"
        if not DECISION_ID.match(decision.id):
            problems.append(f"{where}: id must look like D-1016-k3x (or D-001 from before)")
        if decision_ids.count(decision.id) > 1:
            problems.append(f"{where}: duplicate id")
        if not DATE.match(decision.date):
            problems.append(f"{where}: date must be YYYY-MM-DD")
        if decision.area not in areas:
            problems.append(f"{where}: unknown area {decision.area!r}")
        if not (decision.decision and decision.why and decision.evidence):
            problems.append(f"{where}: needs decision, why and evidence")
        if decision.supersedes and (decision.supersedes == decision.id or decision.supersedes not in decision_ids):
            problems.append(f"{where}: supersedes {decision.supersedes}, which is not another decision")
    return problems


def created_at(moves: list[Move]) -> dict[str, str]:
    """When each job was added: the time of its first move."""
    first: dict[str, str] = {}
    for move in moves:
        first.setdefault(move.id, move.ts)
    return first


def sort_key(item: Item, created: dict[str, str]) -> tuple[int, str, str, str]:
    return (item.priority, item.due or "9999-99-99", created.get(item.id, ""), item.id)


def _row(item: Item, with_note: bool = True) -> str:
    bits = [f"**{item.id}**", f"`{item.area}`", item.title]
    if item.due:
        bits.append(f"(due {item.due})")
    line = " ".join(bits)
    if item.link:
        line += f" · {item.link}"
    if with_note and item.note:
        line += f"  \n  _{item.note}_"
    return f"- {line}"


def _counts_table(by_state: dict[str, list[Item]]) -> list[str]:
    """The counts table, padded the way Prettier pads it, so a project that formats Markdown leaves it alone."""
    heads = ("Doing", "Blocked", "To do", "Held", "Done", "Dropped")
    counts = [str(len(by_state[s])) for s in ("doing", "blocked", "todo", "held", "done", "dropped")]
    widths = [max(len(h), len(c), 3) for h, c in zip(heads, counts)]
    return [
        "| " + " | ".join(h.ljust(w) for h, w in zip(heads, widths)) + " |",
        "| " + " | ".join("-" * w for w in widths) + " |",
        "| " + " | ".join(c.ljust(w) for c, w in zip(counts, widths)) + " |",
    ]


def render_status(
    items: list[Item], moves: list[Move], decisions: list[Decision], *, health: bool = False, recent_done: int = 15
) -> str:
    """The STATUS.md view. Generated, never edited by hand."""
    by_state: dict[str, list[Item]] = {s: [] for s in STATES}
    for item in items:
        by_state[item.state].append(item)
    created = created_at(moves)
    for group in by_state.values():
        group.sort(key=lambda i: sort_key(i, created))

    out = [
        "# Status",
        "",
        "_Generated by `python3 tasks/tool/tasks.py`. Do not edit by hand. After a git merge, run its `status` command. "
        "Rules: [README.md](README.md)._",
        "",
        *_counts_table(by_state),
        "",
    ]

    def section(title: str, rows: list[Item], with_note: bool = True, empty: str = "None.") -> None:
        out.extend([f"## {title}", ""])
        out.extend([_row(i, with_note) for i in rows] or [empty])
        out.append("")

    section("Doing", by_state["doing"])
    section("Blocked", by_state["blocked"])
    section("To do, in priority order", by_state["todo"])

    due_soon = sorted((i for i in items if i.due and i.state in ("todo", "doing", "blocked")), key=lambda i: i.due)
    section("Deadlines", due_soon, with_note=False)

    done_ids = [m.id for m in reversed(moves) if m.to_state == "done"]
    seen: list[str] = []
    for item_id in done_ids:
        if item_id not in seen:
            seen.append(item_id)
    done_items = {i.id: i for i in by_state["done"]}
    recent = [done_items[i] for i in seen if i in done_items][:recent_done]
    section(f"Recently done (last {recent_done})", recent)

    section("Held", by_state["held"])

    out.extend(["## Decisions", ""])
    superseded = {d.supersedes for d in decisions if d.supersedes}
    live = [d for d in decisions if d.id not in superseded]
    if live:
        out.append(
            "Current decisions, newest first. Full log, including superseded ones: [decisions.tsv](decisions.tsv)."
        )
        out.append("")
        for d in sorted(live, key=lambda d: (d.date, d.id), reverse=True):
            out.append(f"- **{d.id}** {d.date} `{d.area}` {d.decision}")
    else:
        out.append("None.")
    out.append("")
    if health:
        out.extend(
            [
                "## Platform health",
                "",
                "One file per Monday digest in [platform-health/](platform-health/), named by date. The newest file is the latest report.",
                "",
            ]
        )
    return "\n".join(out)
