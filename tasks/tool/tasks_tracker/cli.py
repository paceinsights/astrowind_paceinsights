"""File IO and commands for the tracker. The only writer of the tasks/ TSV files and STATUS.md."""

from __future__ import annotations

import argparse
import configparser
import csv
import os
import subprocess
import sys
import tempfile
from dataclasses import astuple
from datetime import datetime, timezone
from pathlib import Path

from .core import (
    AREA,
    DECISION_COLUMNS,
    ITEM_COLUMNS,
    MOVE_COLUMNS,
    STATES,
    Decision,
    Item,
    Move,
    Settings,
    TrackerError,
    add_decision,
    add_item,
    edit_item,
    move_item,
    render_status,
    settle,
    validate,
)
from . import vendor
from .template import README

FOLDER = "tasks"
SETTINGS_FILE = "tracker.ini"
CMD = "python3 tasks/tool/tasks.py"
REGISTRY_COLUMNS = ("path", "branch", "added")
GITATTRIBUTES = """# Written by the tasks command. When two branches both change the job lists, git keeps both sides' lines
# instead of stopping with a conflict. The next tasks command tidies them: the newest version of a job wins,
# and two different moves of the same job are reported by tasks check.
*.tsv merge=union
STATUS.md merge=union
"""


def parse_areas(text: str) -> tuple[str, ...]:
    areas = tuple(dict.fromkeys(a.strip() for a in text.split(",") if a.strip()))
    if not areas:
        raise TrackerError("at least one area is needed, e.g. --areas frontend,backend,ops")
    bad = [a for a in areas if not AREA.match(a)]
    if bad:
        raise TrackerError(f"areas use lowercase letters, digits and dashes, got {', '.join(bad)}")
    return areas


def load_settings(root: Path) -> Settings:
    parser = configparser.ConfigParser()
    try:
        parser.read_string((root / SETTINGS_FILE).read_text(encoding="utf-8"))
        section = parser["tracker"]
        name, areas = section["name"].strip(), section["areas"]
    except (configparser.Error, KeyError):
        raise TrackerError(f"{root / SETTINGS_FILE} needs a [tracker] section with name and areas") from None
    if not name:
        raise TrackerError(f"{root / SETTINGS_FILE}: name is empty")
    return Settings(name=name, areas=parse_areas(areas))


def write_settings(root: Path, settings: Settings) -> None:
    (root / SETTINGS_FILE).write_text(
        "# Settings for the tasks tracker. The one file in this folder you edit by hand.\n"
        "# To add an area, add it to the list. To remove one, first move its jobs to another area.\n"
        "[tracker]\n"
        f"name = {settings.name}\n"
        f"areas = {', '.join(settings.areas)}\n",
        encoding="utf-8",
    )


def find_root(start: Path) -> Path:
    """The nearest tasks/ folder with a tracker.ini, looking in start and then each folder above it."""
    for folder in (start, *start.parents):
        if (folder / FOLDER / SETTINGS_FILE).is_file():
            return folder / FOLDER
    raise TrackerError(
        f"no {FOLDER}/{SETTINGS_FILE} in {start} or any folder above it. "
        'To set this project up, run at its top on Samir\'s Mac: tasks init --name "Project name" --areas a,b,c'
    )


def _git(cwd: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def project_top(start: Path) -> Path:
    top = _git(start, "rev-parse", "--show-toplevel")
    return Path(top) if top else start


def register(registry: Path, project: Path, today: str) -> None:
    """Add a project to jobs-tracker's list of projects, which update_projects.py works through."""
    rows = Store._read(registry, REGISTRY_COLUMNS)
    if any(Path(r[0]) == project for r in rows):
        return
    branch = _git(project, "symbolic-ref", "--short", "HEAD") or "main"
    Store._write(registry, REGISTRY_COLUMNS, [tuple(r) for r in rows] + [(str(project), branch, today)])
    print(f"Added {project} to {registry.name} (updates go on {branch}; edit the file to change it)")


class Store:
    def __init__(self, root: Path, settings: Settings) -> None:
        self.root = root
        self.settings = settings
        self.items_path = root / "items.tsv"
        self.history_path = root / "history.tsv"
        self.decisions_path = root / "decisions.tsv"
        self.status_path = root / "STATUS.md"
        self.attributes_path = root / ".gitattributes"
        self.needs_tidy = False

    @property
    def has_health(self) -> bool:
        return (self.root / "platform-health").is_dir()

    @staticmethod
    def _read(path: Path, columns: tuple[str, ...]) -> list[list[str]]:
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None))
        if not rows:
            return []
        if tuple(rows[0]) != columns:
            raise TrackerError(f"{path.name}: header must be {' '.join(columns)}")
        body = rows[1:]
        for n, row in enumerate(body, start=2):
            if len(row) != len(columns):
                raise TrackerError(f"{path.name} line {n}: expected {len(columns)} columns, found {len(row)}")
        return body

    @staticmethod
    def _stage(path: Path, columns: tuple[str, ...], rows: list[tuple]) -> str:
        """Write the table to a temporary file next to it and return its name. Quote marks are plain text:
        cells can't hold tabs or line breaks (clean_cell), so nothing needs quoting."""
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
        try:
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_NONE, quotechar=None, lineterminator="\n")
                writer.writerow(columns)
                writer.writerows([[str(c) for c in row] for row in rows])
        except BaseException:
            os.unlink(tmp)
            raise
        return tmp

    @staticmethod
    def _write(path: Path, columns: tuple[str, ...], rows: list[tuple]) -> None:
        os.replace(Store._stage(path, columns, rows), path)

    def load(self) -> tuple[list[Item], list[Move], list[Decision]]:
        items = []
        for row in self._read(self.items_path, ITEM_COLUMNS):
            values = dict(zip(ITEM_COLUMNS, row))
            try:
                values["priority"] = int(values["priority"])
            except ValueError:
                raise TrackerError(f"items.tsv {values['id']}: priority must be a whole number") from None
            items.append(Item(**values))
        moves = [Move(*row) for row in self._read(self.history_path, MOVE_COLUMNS)]
        decisions = [Decision(*row) for row in self._read(self.decisions_path, DECISION_COLUMNS)]
        items, moves, decisions, self.needs_tidy = settle(items, moves, decisions)
        return items, moves, decisions

    def status(self, items: list[Item], moves: list[Move], decisions: list[Decision]) -> str:
        return render_status(items, moves, decisions, health=self.has_health)

    def save(self, items: list[Item], moves: list[Move], decisions: list[Decision]) -> None:
        problems = validate(items, moves, decisions, self.settings.areas)
        if problems:
            raise TrackerError("refusing to save, the result breaks the rules:\n" + "\n".join(problems))
        # Write every table to a temporary file first, then swap them all in: a failure leaves the old files whole.
        staged: list[tuple[str, Path]] = []
        try:
            for path, columns, rows in (
                (self.items_path, ITEM_COLUMNS, [astuple(i) for i in items]),
                (self.history_path, MOVE_COLUMNS, [astuple(m) for m in moves]),
                (self.decisions_path, DECISION_COLUMNS, [astuple(d) for d in decisions]),
            ):
                staged.append((self._stage(path, columns, rows), path))
        except BaseException:
            for tmp, _ in staged:
                os.unlink(tmp)
            raise
        for tmp, path in staged:
            os.replace(tmp, path)
        self.status_path.write_text(self.status(items, moves, decisions), encoding="utf-8")
        if not self.attributes_path.exists():
            self.attributes_path.write_text(GITATTRIBUTES, encoding="utf-8")
        self.needs_tidy = False


def _now() -> tuple[str, str]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return now.date().isoformat(), now.strftime("%Y-%m-%dT%H:%M:%SZ")


def _find(items: list[Item], item_id: str) -> int:
    for n, item in enumerate(items):
        if item.id == item_id:
            return n
    raise TrackerError(f"no item {item_id}")


def _print_items(items: list[Item]) -> None:
    for i in sorted(items, key=lambda i: (STATES.index(i.state), i.priority, i.id)):
        due = f" due {i.due}" if i.due else ""
        print(f"{i.id}\t{i.state}\tp{i.priority}\t{i.area}\t{i.title}{due}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tasks", description="Jobs-to-be-done tracker. See tasks/README.md.")
    parser.add_argument("--dir", type=Path, help="the tasks/ folder, if not the nearest one above here")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="set up tasks/ in this project, or adopt an existing tasks/ folder")
    p.add_argument("--name", required=True, help="the project name shown on the board")
    p.add_argument("--areas", default="general", help="comma-separated, e.g. frontend,backend,ops")

    p = sub.add_parser("add", help="add a job")
    p.add_argument("area")
    p.add_argument("title")
    p.add_argument("--priority", type=int, required=True, help="1 is most urgent")
    p.add_argument("--state", choices=STATES, default="todo")
    p.add_argument("--due", default="", help="YYYY-MM-DD")
    p.add_argument("--link", default="")
    p.add_argument("--note", default="")

    p = sub.add_parser("move", help="change a job's state")
    p.add_argument("id")
    p.add_argument("state", choices=STATES)
    p.add_argument("--note", default="", help="why, or the evidence when moving to done")

    p = sub.add_parser("edit", help="change a job's title, area, priority, due, link or note (not its state)")
    p.add_argument("id")
    for flag in ("title", "area", "due", "link", "note"):
        p.add_argument(f"--{flag}")
    p.add_argument("--priority", type=int)

    p = sub.add_parser("decide", help="record a decision (append-only)")
    p.add_argument("area")
    p.add_argument("decision")
    p.add_argument("--why", required=True)
    p.add_argument("--evidence", required=True, help="doc path, commit, PR or 'chat YYYY-MM-DD'")
    p.add_argument("--supersedes", default="")
    p.add_argument("--date", default="", help="YYYY-MM-DD, defaults to today")

    p = sub.add_parser("list", help="print jobs")
    p.add_argument("--state", choices=STATES)
    p.add_argument("--area")

    sub.add_parser("status", help="regenerate STATUS.md, and tidy the tables after a git merge")
    sub.add_parser("check", help="verify the files keep every rule and STATUS.md is current")
    p = sub.add_parser("serve", help="open a read-only board at http://localhost:8765")
    p.add_argument("--port", type=int, default=8765)
    return parser


def init(root: Path, name: str, areas_text: str, registry: Path | None) -> int:
    if (root / SETTINGS_FILE).exists():
        raise TrackerError(f"{root / SETTINGS_FILE} already exists. Edit it to change the name or areas")
    adopting = (root / "items.tsv").exists()
    if root.exists() and any(root.iterdir()) and not adopting:
        raise TrackerError(f"{root} already exists and is not a tracker folder. Choose another with --dir")
    settings = Settings(name=name.strip(), areas=parse_areas(areas_text))
    if not settings.name:
        raise TrackerError("--name cannot be empty")
    store = Store(root, settings)
    items, moves, decisions = store.load()
    problems = validate(items, moves, decisions, settings.areas)
    if problems:
        raise TrackerError("the existing files do not fit these settings:\n" + "\n".join(problems))
    root.mkdir(parents=True, exist_ok=True)
    write_settings(root, settings)
    if not (root / "README.md").exists():
        (root / "README.md").write_text(README.format(name=settings.name), encoding="utf-8")
    store.save(items, moves, decisions)
    vendor.install(root)
    verb = f"Adopted {len(items)} jobs and {len(decisions)} decisions in" if adopting else "Set up"
    print(f"{verb} {root} for {settings.name}. Areas: {', '.join(settings.areas)}")
    print(f"The tracker's own copy is in {root / vendor.TOOL}. On any computer: {CMD} <command>")
    if registry:
        register(registry, root.parent, _now()[0])
    return 0


def run(argv: list[str] | None, home: Path | None, registry: Path | None) -> int:
    """home is the project's tasks/ folder when this is the project's own copy (tasks/tool/tasks.py)."""
    args = build_parser().parse_args(argv)
    if args.command == "init":
        if home:
            raise TrackerError(f"{home} is already set up")
        return init(args.dir or project_top(Path.cwd()) / FOLDER, args.name, args.areas, registry)

    root = args.dir or home or find_root(Path.cwd())
    if not (root / SETTINGS_FILE).is_file():
        raise TrackerError(f"{root} has no {SETTINGS_FILE}. Set it up with: tasks --dir {root} init --name ...")
    store = Store(root, load_settings(root))
    areas = store.settings.areas
    today, now = _now()
    items, moves, decisions = store.load()

    if args.command == "serve":
        from .web import serve

        serve(store, args.port)
        return 0

    if args.command == "check":
        problems = validate(items, moves, decisions, areas)
        expected = store.status(items, moves, decisions)
        actual = store.status_path.read_text(encoding="utf-8") if store.status_path.exists() else ""
        if actual != expected:
            problems.append(f"STATUS.md is out of date or was edited by hand. Run: {CMD} status")
        if store.needs_tidy:
            problems.append(f"the tables still hold both sides of a git merge. Run: {CMD} status")
        if not store.attributes_path.exists():
            problems.append(f"tasks/.gitattributes is missing, so branches can clash. Run: {CMD} status")
        problems.extend(vendor.check_copy(root))
        for problem in problems:
            print(problem, file=sys.stderr)
        if not problems:
            print(f"tracker ok: {len(items)} jobs, {len(moves)} moves, {len(decisions)} decisions")
        return 1 if problems else 0

    if args.command == "list":
        _print_items(
            [i for i in items if (not args.state or i.state == args.state) and (not args.area or i.area == args.area)]
        )
        return 0

    if args.command == "add":
        item, move = add_item(
            items,
            areas=areas,
            area=args.area,
            title=args.title,
            priority=args.priority,
            state=args.state,
            due=args.due,
            link=args.link,
            note=args.note,
            today=today,
            now=now,
        )
        items.append(item)
        moves.append(move)
        print(f"added {item.id} ({item.state})")
    elif args.command == "move":
        n = _find(items, args.id)
        items[n], move = move_item(items[n], args.state, note=args.note, today=today, now=now)
        moves.append(move)
        print(f"{move.id}: {move.from_state} -> {move.to_state}")
    elif args.command == "edit":
        n = _find(items, args.id)
        changes = {k: getattr(args, k) for k in ("title", "area", "due", "link", "note", "priority")}
        changes = {k: v for k, v in changes.items() if v is not None}
        if not changes:
            raise TrackerError("nothing to change")
        items[n] = edit_item(items[n], areas=areas, now=now, **changes)
        print(f"edited {args.id}")
    elif args.command == "decide":
        decision = add_decision(
            decisions,
            areas=areas,
            area=args.area,
            decision=args.decision,
            why=args.why,
            evidence=args.evidence,
            supersedes=args.supersedes,
            date=args.date or today,
            today=today,
        )
        decisions.append(decision)
        print(f"recorded {decision.id}")

    store.save(items, moves, decisions)
    return 0


def main(argv: list[str] | None = None, home: Path | None = None, registry: Path | None = None) -> int:
    try:
        return run(argv, home, registry)
    except TrackerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
