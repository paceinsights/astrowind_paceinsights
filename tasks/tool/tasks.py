"""This project's copy of the tasks tracker: python3 tasks/tool/tasks.py <command>. See tasks/README.md.

Do not edit anything in tasks/tool/. The update script in paceinsights/jobs-tracker replaces it.
"""

import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tasks_tracker.cli import main  # noqa: E402

raise SystemExit(main(sys.argv[1:], home=Path(__file__).resolve().parents[1]))
