# Jobs to be done

The one place that says what is being done for Pace Insights, what is next, what is done and what was decided.

**Read [STATUS.md](STATUS.md).** To see it as a board:

```bash
python3 tasks/tool/tasks.py serve
```

Then open http://localhost:8765. The board is read-only. To run two boards at once: `serve --port 8766`.

## The command

The tracker's code is inside this project, in `tasks/tool/`, so it runs on any computer and in any session with
plain Python 3.9 or later. Run it from the top of the project:

```bash
python3 tasks/tool/tasks.py <command>
```

On Samir's Mac, `tasks <command>` does the same from anywhere in the project.

Never edit `tasks/tool/`. It comes from paceinsights/jobs-tracker, whose `update_projects.py` replaces it in
every project. `check` fails if it was changed by hand.

## Files

| File             | What it holds                                                                       | Who writes it                     |
| ---------------- | ----------------------------------------------------------------------------------- | --------------------------------- |
| `tracker.ini`    | The project name and its areas                                                      | You, by hand                      |
| `items.tsv`      | Every job, one row each: id, state, priority, area, title, due, link, note, updated | the command only                  |
| `history.tsv`    | Every state change. Only ever added to                                              | the command only                  |
| `decisions.tsv`  | Decisions, with why and evidence. Only ever added to                                | the command only                  |
| `STATUS.md`      | The readable view, generated from the three tables                                  | the command only                  |
| `.gitattributes` | Tells git to keep both sides when two branches change the tables                    | the command only                  |
| `tool/`          | The tracker's code                                                                  | jobs-tracker's update script only |

Do not edit the TSV files or STATUS.md by hand. `check` fails on a hand edit that breaks a rule, or on a
STATUS.md that is out of date.

## States

| State     | Means                             | Can move to                         |
| --------- | --------------------------------- | ----------------------------------- |
| `todo`    | Agreed and waiting                | doing, blocked, held, done, dropped |
| `doing`   | Being worked on now               | todo, blocked, held, done, dropped  |
| `blocked` | Started, but waiting on something | todo, doing, held, dropped          |
| `held`    | Decided not now                   | todo, dropped                       |
| `done`    | Finished                          | todo (reopen)                       |
| `dropped` | Not doing it                      | todo (revive)                       |

Moving to `blocked`, `held` or `dropped` needs a note saying why. Moving to `done` needs a note with the
evidence: a PR, release or commit. The command refuses any other move.

Priority is a number. 1 is most urgent. Jobs are named by the day they were added plus three random characters,
such as `T-1016-k3x`, so two branches adding jobs at the same time never pick the same name.

Areas are listed in `tracker.ini`. To add one, add it to the list there.

## Commands

```bash
python3 tasks/tool/tasks.py list --state todo
python3 tasks/tool/tasks.py add general "Write the first job" --priority 2 --due 2026-12-01 --link docs/plan.md
python3 tasks/tool/tasks.py move T-1016-k3x doing
python3 tasks/tool/tasks.py move T-1016-k3x done --note "PR #12, released v1.2.0"
python3 tasks/tool/tasks.py move T-1016-m7p held --note "after the launch"
python3 tasks/tool/tasks.py edit T-1016-k3x --priority 1
python3 tasks/tool/tasks.py decide general "Keep it simple" --why "solo project" --evidence "chat 2026-10-16"
python3 tasks/tool/tasks.py decide general "New rule" --why "..." --evidence "..." --supersedes D-1016-a2b
python3 tasks/tool/tasks.py status
python3 tasks/tool/tasks.py check
```

Every command that changes something regenerates STATUS.md. A decision is never edited or deleted. A new
decision that replaces an old one names it with `--supersedes`.

## When two branches both changed the job list

Git merges on a computer keep both sides, because of `.gitattributes`. GitHub's own merge button does not, so a
pull request can show a conflict in `tasks/`. To fix it, on the pull request's branch:

```bash
git merge origin/<the branch the PR goes into>
python3 tasks/tool/tasks.py status
python3 tasks/tool/tasks.py check
git commit -am "tasks: merge the job lists"
git push
```

The merge goes through without stopping, `status` tidies the tables, and the pull request can be merged. If
`check` then reports a job that was moved two different ways, ask Samir which one stands.

## For agents

- Read STATUS.md first. Before changing how something works, check its decisions. If a change would go
  against one, stop and ask Samir; if he agrees, record a new decision that supersedes it.
- Start a job with `move <id> doing` and finish it with `move <id> done --note "<evidence>"`.
- Record a decision made in chat with `decide`, evidence `chat <date>`.
- Run `check` before committing changes to `tasks/`.
- Long notes belong in `docs/`. The job row links to them.
