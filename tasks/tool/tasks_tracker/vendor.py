"""The copy of the tracker each project carries in tasks/tool/, so it runs on any computer with plain Python.

jobs-tracker's update_projects.py replaces the copy. Nobody edits it by hand: check compares it with the
fingerprint in tasks/tool/VERSION.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CODE_FILES = ("__init__.py", "cli.py", "core.py", "template.py", "vendor.py", "web.py")
TOOL = "tool"
ENTRY_NAME = "tasks.py"
ENTRY = '''"""This project's copy of the tasks tracker: python3 tasks/tool/tasks.py <command>. See tasks/README.md.

Do not edit anything in tasks/tool/. The update script in paceinsights/jobs-tracker replaces it.
"""

import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tasks_tracker.cli import main  # noqa: E402

raise SystemExit(main(sys.argv[1:], home=Path(__file__).resolve().parents[1]))
'''


def _fingerprint(entry: str, files: dict[str, str]) -> str:
    digest = hashlib.sha256(entry.encode())
    for name in CODE_FILES:
        digest.update(name.encode() + b"\0" + files[name].encode())
    return digest.hexdigest()[:12]


def source_fingerprint() -> str:
    """The fingerprint of the code that is running now."""
    return _fingerprint(ENTRY, {n: (PACKAGE / n).read_text(encoding="utf-8") for n in CODE_FILES})


def copy_fingerprint(root: Path) -> str:
    """The fingerprint of a project's copy as it is on disk."""
    tool = root / TOOL
    return _fingerprint(
        (tool / ENTRY_NAME).read_text(encoding="utf-8"),
        {n: (tool / "tasks_tracker" / n).read_text(encoding="utf-8") for n in CODE_FILES},
    )


def recorded_fingerprint(root: Path) -> str:
    """The fingerprint written in tasks/tool/VERSION when the copy was installed, or "" if there is no copy."""
    version = root / TOOL / "VERSION"
    if not version.is_file():
        return ""
    for line in version.read_text(encoding="utf-8").splitlines():
        if line.startswith("fingerprint = "):
            return line.split("=", 1)[1].strip()
    return ""


def install(root: Path) -> str:
    """Replace the project's tasks/tool/ with the running code. Returns the new fingerprint."""
    tool = root / TOOL
    if tool.exists():
        shutil.rmtree(tool)
    (tool / "tasks_tracker").mkdir(parents=True)
    for name in CODE_FILES:
        shutil.copyfile(PACKAGE / name, tool / "tasks_tracker" / name)
    (tool / ENTRY_NAME).write_text(ENTRY, encoding="utf-8")
    fingerprint = source_fingerprint()
    (tool / "VERSION").write_text(
        "# The tasks tracker, copied from paceinsights/jobs-tracker by its update script. Do not edit this folder.\n"
        f"fingerprint = {fingerprint}\n",
        encoding="utf-8",
    )
    return fingerprint


def check_copy(root: Path) -> list[str]:
    recorded = recorded_fingerprint(root)
    if not recorded:
        return ["tasks/tool/VERSION is missing. Reinstall the copy with jobs-tracker's update_projects.py"]
    try:
        actual = copy_fingerprint(root)
    except FileNotFoundError as exc:
        return [f"tasks/tool is missing {Path(exc.filename).name}. Reinstall it with jobs-tracker's update_projects.py"]
    if actual != recorded:
        return [
            "the tracker code in tasks/tool was changed by hand. Only jobs-tracker's update_projects.py changes it: "
            "put the change in jobs-tracker, then run the update"
        ]
    return []
