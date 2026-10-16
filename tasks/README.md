# Jobs to be done

The one place that says what is being done for Pace Insights, what is next, what is done and what was decided.

**Read [STATUS.md](STATUS.md)**, or run the board:

```bash
tasks serve
```

Then open http://localhost:8765. The board is read-only. It reads the files below each time the page loads.
To run two boards at once, give one another port: `tasks serve --port 8766`.

The `tasks` command is shared by every project. Its code and install steps live in `~/Projects/jobs-tracker`.

## Files

| File            | What it holds                                                                       | Who writes it |
| --------------- | ----------------------------------------------------------------------------------- | ------------- |
| `tracker.ini`   | The project name and its areas                                                      | You, by hand  |
| `items.tsv`     | Every job, one row each: id, state, priority, area, title, due, link, note, updated | `tasks` only  |
| `history.tsv`   | Every state change, oldest first. Only ever added to                                | `tasks` only  |
| `decisions.tsv` | Decisions, with why and evidence. Only ever added to                                | `tasks` only  |
| `STATUS.md`     | The readable view, generated from the three tables                                  | `tasks` only  |

Do not edit the TSV files or STATUS.md by hand. `tasks check` fails on a hand edit that breaks a rule, or on a STATUS.md that is out of date.

## States

| State     | Means                             | Can move to                         |
| --------- | --------------------------------- | ----------------------------------- |
| `todo`    | Agreed and waiting                | doing, blocked, held, done, dropped |
| `doing`   | Being worked on now               | todo, blocked, held, done, dropped  |
| `blocked` | Started, but waiting on something | todo, doing, held, dropped          |
| `held`    | Decided not now                   | todo, dropped                       |
| `done`    | Finished                          | todo (reopen)                       |
| `dropped` | Not doing it                      | todo (revive)                       |

Moving to `blocked`, `held` or `dropped` needs a note saying why. Moving to `done` needs a note with the evidence: a PR, release or commit. The command refuses any other move.

Priority is a number. 1 is most urgent. The board and STATUS.md sort by priority, then due date.

Areas are listed in `tracker.ini`. To add one, add it to the list there.

## Commands

Run them from anywhere inside the project. `tasks` finds this folder by looking upwards.

```bash
tasks list --state todo
tasks add general "Write the first job" --priority 2 --due 2026-12-01 --link docs/plan.md
tasks move T-001 doing
tasks move T-001 done --note "PR #12, released v1.2.0"
tasks move T-002 held --note "after the launch"
tasks edit T-001 --priority 1
tasks decide general "Keep it simple" --why "solo project" --evidence "chat 2026-10-16"
tasks decide general "New rule" --why "..." --evidence "..." --supersedes D-001
tasks check
```

Every command that changes something regenerates STATUS.md. A decision is never edited or deleted. A new decision that replaces an old one names it with `--supersedes`.

## For agents

- Read STATUS.md first.
- Start a job with `tasks move <id> doing` and finish it with `tasks move <id> done --note "<evidence>"`.
- Record a decision made in chat with `tasks decide`, evidence `chat <date>`.
- Long notes belong in `docs/`. The job row links to them.
