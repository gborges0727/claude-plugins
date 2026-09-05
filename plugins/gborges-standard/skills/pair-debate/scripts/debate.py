#!/usr/bin/env python3
"""Run two architects, Claude Fable and Codex Astra, against one problem.

The pair-debate skill starts this script in the background. The script
owns the whole conversation: it starts one Claude session and one Codex
thread, hands each architect the other's last message, appends every turn
to a transcript, and writes one JSON line per event to events.jsonl so the
orchestrator can watch without reading the turns.

A run has three phases.

  draft    Both architects write an independent proposal at the same time,
           each blind to the other's. Neither edits a tracked file yet.
  define   They trade drafts and argue until both agree on a definition of
           done. The script then writes phase "awaiting-approval" to
           state.json and exits, so the orchestrator can show the user.
  work     `resume` continues the run. They alternate turns, editing the
           shared worktree, until both consecutive replies say agreed.

Every architect reply ends with a status line the script reads:

  STATUS: continue | agreed
  CHECK: pass | fail | none      (work phase only)

Usage:
  debate.py start  --repo DIR --topic SLUG --brief FILE [--out REL] [--state DIR]
  debate.py resume --state DIR [--note FILE]
  debate.py status --state DIR
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

CONFIG = Path.home() / ".claude" / "gborges-standard.json"

# PAIR_DEBATE_SMOKE=1 runs the loop on cheap models at low effort, so the
# script can be tested end to end without spending the two xhigh rungs.
SMOKE = os.environ.get("PAIR_DEBATE_SMOKE") == "1"
STATE_ROOT = Path.home() / ".claude" / "gborges-standard" / "pair-debate"

CLAUDE_NAME = "claude"
CODEX_NAME = "codex"

STATUS_LINE = re.compile(r"^\s*STATUS:\s*(continue|agreed)\s*$", re.IGNORECASE | re.MULTILINE)
CHECK_LINE = re.compile(r"^\s*CHECK:\s*(pass|fail|none)\s*$", re.IGNORECASE | re.MULTILINE)

# `codex exec resume` has no -C or -s flag. The thread remembers its
# working directory, and the sandbox comes from config, so both forms of
# the command set the sandbox through -c.
CODEX_FLAGS = [
    "-c", "sandbox_mode=workspace-write",
    "-c", "approval_policy=never",
    "-c", "sandbox_workspace_write.network_access=true",
    "-c", "mcp_servers.playwright.enabled=false",
    "-c", "mcp_servers.chrome-devtools.enabled=false",
]


# ---------------------------------------------------------------- state ---


class Run:
    def __init__(self, state_dir):
        self.dir = Path(state_dir)
        self.file = self.dir / "state.json"
        self.data = {}
        if self.file.exists():
            self.data = json.loads(self.file.read_text(encoding="utf-8"))

    def save(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def event(self, name, **detail):
        line = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": name}
        line.update(detail)
        text = json.dumps(line)
        with (self.dir / "events.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(text, flush=True)

    @property
    def worktree(self):
        return Path(self.data["worktree"])

    @property
    def room(self):
        return self.worktree / self.data["out"]


# ---------------------------------------------------------- architects ---


def claude_model():
    try:
        parsed = json.loads(CONFIG.read_text(encoding="utf-8"))
        if parsed.get("fable") is False:
            return "opus"
    except (OSError, ValueError):
        pass
    return "fable"


def run_claude(run, prompt, label):
    """One Claude turn. Returns the reply text. Keeps the session id."""
    model = "sonnet" if SMOKE else claude_model()
    cmd = [
        "claude", "-p",
        "--model", model,
        "--effort", "low" if SMOKE else "xhigh",
        "--dangerously-skip-permissions",
        "--output-format", "json",
    ]
    session = run.data.get("claude_session")
    if session:
        cmd += ["--resume", session]
    (run.dir / f"{label}.prompt.md").write_text(prompt, encoding="utf-8")
    proc = subprocess.run(
        cmd, input=prompt, text=True, capture_output=True, cwd=run.worktree,
    )
    (run.dir / f"{label}.raw.json").write_text(proc.stdout, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[-2000:]}")
    try:
        parsed = json.loads(proc.stdout)
    except ValueError:
        raise RuntimeError("claude printed no JSON result; see " + str(run.dir / f"{label}.raw.json"))
    if not session and parsed.get("session_id"):
        run.data["claude_session"] = parsed["session_id"]
        run.save()
    reply = parsed.get("result") or ""
    (run.dir / f"{label}.md").write_text(reply, encoding="utf-8")
    return reply


def run_codex(run, prompt, label):
    """One Codex turn. Returns the reply text. Keeps the thread id."""
    out = run.dir / f"{label}.md"
    log = run.dir / f"{label}.jsonl"
    (run.dir / f"{label}.prompt.md").write_text(prompt, encoding="utf-8")
    trust = f'projects."{run.worktree}".trust_level="trusted"'
    thread = run.data.get("codex_thread")
    if thread:
        cmd = ["codex", "exec", "resume", thread]
    else:
        cmd = ["codex", "exec", "-C", str(run.worktree)]
    cmd += [
        "-m", "gpt-5.6-luna" if SMOKE else "gpt-6-astra",
        "-c", "model_reasoning_effort=" + ("low" if SMOKE else "xhigh"),
        "-c", trust,
        *CODEX_FLAGS,
        "--json", "-o", str(out), "-",
    ]
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            cmd, input=prompt, text=True, stdout=fh, stderr=subprocess.STDOUT,
            cwd=run.worktree,
        )
    if not thread:
        try:
            first = log.read_text(encoding="utf-8").splitlines()[0]
            thread_id = json.loads(first).get("thread_id")
        except (OSError, ValueError, IndexError):
            thread_id = None
        if thread_id:
            run.data["codex_thread"] = thread_id
            run.save()
    if proc.returncode != 0 or not out.exists() or not out.read_text(encoding="utf-8").strip():
        raise RuntimeError(f"codex exited {proc.returncode} with no final message; see {log}")
    return out.read_text(encoding="utf-8")


RUNNERS = {CLAUDE_NAME: run_claude, CODEX_NAME: run_codex}


def other(name):
    return CODEX_NAME if name == CLAUDE_NAME else CLAUDE_NAME


def display(name):
    return "Fable" if name == CLAUDE_NAME else "Astra"


# ------------------------------------------------------------- prompts ---


def preamble(run, name):
    room = run.data["out"]
    if name == CLAUDE_NAME:
        delegate = (
            "When a subtask stands alone and a command checks it, hand it to the "
            "gborges-standard:opus-medium agent through the Agent tool and wait for it "
            "to finish before you end your turn. Never spawn any other agent type."
        )
    else:
        delegate = (
            "When a subtask stands alone and a command checks it, hand it to your "
            "sol-xhigh subagent and wait for it to finish before you end your turn. "
            "Never spawn any other agent."
        )
    return f"""You are {display(name)}, one of two architects working the problem below. The
other architect is {display(other(name))}, a different model with a different style. A script
carries your messages between you. You are peers. Neither of you outranks the other, and the
run ends only when you both agree.

Working directory: {run.worktree} (a git worktree on branch {run.data['branch']}).
Shared room folder for drafts, the transcript, and the definition of done: {room}/
Your scratch folder for experiments that should not be committed: {run.dir}/scratch-{name}/

{delegate}

Commit your own edits before you end a turn, with a Conventional Commits subject in single
quotes and no AI trailer or footer. Write every message as plain prose for a sharp coworker:
one idea per sentence, concrete verbs, real file names, no headers unless the message runs
long. Say what you did, what you found, and what you disagree with, and state each
disagreement as a claim the other architect can test.
"""


def draft_prompt(run, name, brief):
    return preamble(run, name) + f"""
## The problem

{brief}

## This turn: your independent draft

Write your own proposal before you see the other architect's. Read the repo, run experiments
in your scratch folder, and delegate legwork if it helps. Do not edit any tracked file in
this turn, and do not read {run.data['out']}/drafts/. Write the proposal to
{run.data['out']}/drafts/{name}.md: what you would build, why, what you rejected, and the
open questions the other architect should answer. End your reply with a short summary of
the draft, then the line:

STATUS: continue
"""


def define_prompt(run, name, other_draft, other_message, first):
    parts = []
    if first:
        parts.append(
            f"The drafts are in. Here is {display(other(name))}'s draft:\n\n---\n{other_draft}\n---\n"
        )
    if other_message:
        parts.append(f"{display(other(name))} says:\n\n---\n{other_message}\n---\n")
    parts.append(f"""## This phase: agree on the definition of done

Before either of you builds anything, you both have to agree, in writing, what finished
means for this problem. Argue over the drafts and converge on one document. For a build ask
the definition names the check: one command, run from the worktree, whose exit code says
whether the work is done, plus the metric and threshold it enforces. For a document ask the
definition names the document and what it has to cover.

When you agree with the current proposal in full, write it to
{run.data['out']}/definition-of-done.md, write the check command alone to
{run.data['out']}/check.sh (a comment and `exit 0` if the ask has no check), commit both, and
end your reply with the line:

STATUS: agreed

Otherwise say what you would change and why, and end with:

STATUS: continue
""")
    return "\n".join(parts)


def work_prompt(run, name, other_message, note, first):
    parts = []
    if first:
        parts.append(
            "The user approved the definition of done. Read "
            f"{run.data['out']}/definition-of-done.md and {run.data['out']}/check.sh before you start.\n"
        )
    if note:
        parts.append(f"The user added a note when they approved it:\n\n---\n{note}\n---\n")
    if other_message:
        parts.append(f"{display(other(name))} says:\n\n---\n{other_message}\n---\n")
    parts.append(f"""## This phase: do the work

Only you edit the worktree during your turn. Start by reading what {display(other(name))}
changed since your last turn (`git log` and `git diff`). Build, test, and argue in the same
message. Run `bash {run.data['out']}/check.sh` whenever you claim progress and quote its
result.

End every reply with two lines. The first is `CHECK: pass`, `CHECK: fail`, or `CHECK: none`
if you did not run it this turn. The second is `STATUS: agreed` only when the check passes
and you have nothing left to change or contest, and `STATUS: continue` otherwise. The run
ends when you both say agreed in consecutive turns.
""")
    return "\n".join(parts)


# -------------------------------------------------------------- phases ---


def parse_status(reply):
    match = STATUS_LINE.findall(reply)
    return match[-1].lower() if match else None


def parse_check(reply):
    match = CHECK_LINE.findall(reply)
    return match[-1].lower() if match else None


def append_transcript(run, name, phase, reply):
    run.data["turn"] = run.data.get("turn", 0) + 1
    run.save()
    path = run.room / "transcript.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## Turn {run.data['turn']} ({phase}), {display(name)}\n\n{reply.rstrip()}\n")


def commit_room(run, subject):
    rel = run.data["out"]
    subprocess.run(["git", "add", "-A", rel], cwd=run.worktree, check=False)
    subprocess.run(
        ["git", "commit", "-q", "-m", subject, "--", rel],
        cwd=run.worktree, check=False, capture_output=True,
    )


def take_turn(run, name, phase, prompt):
    label = f"{run.data.get('turn', 0) + 1:03d}-{phase}-{name}"
    run.event("turn-start", who=display(name), phase=phase, turn=run.data.get("turn", 0) + 1)
    try:
        reply = RUNNERS[name](run, prompt, label)
    except RuntimeError as err:
        run.data["phase"] = "error"
        run.save()
        run.event("error", who=display(name), phase=phase, detail=str(err))
        sys.exit(1)
    append_transcript(run, name, phase, reply)
    status = parse_status(reply)
    if status is None:
        run.event("missing-status", who=display(name), turn=run.data["turn"])
        status = "continue"
    check = parse_check(reply) if phase == "work" else None
    run.event("turn-end", who=display(name), phase=phase, turn=run.data["turn"], status=status, check=check)
    return reply, status, check


def phase_draft(run, brief):
    run.data["phase"] = "draft"
    run.save()
    run.event("phase", phase="draft")
    (run.room / "drafts").mkdir(parents=True, exist_ok=True)
    for name in (CLAUDE_NAME, CODEX_NAME):
        (run.dir / f"scratch-{name}").mkdir(parents=True, exist_ok=True)
    results = {}
    errors = {}

    def worker(name):
        try:
            results[name] = RUNNERS[name](run, draft_prompt(run, name, brief), f"000-draft-{name}")
        except RuntimeError as err:
            errors[name] = str(err)

    threads = [threading.Thread(target=worker, args=(n,)) for n in (CLAUDE_NAME, CODEX_NAME)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        run.data["phase"] = "error"
        run.save()
        for name, err in errors.items():
            run.event("error", who=display(name), phase="draft", detail=err)
        sys.exit(1)
    for name in (CLAUDE_NAME, CODEX_NAME):
        append_transcript(run, name, "draft", results[name])
    commit_room(run, "docs(pair-debate): add both architects' drafts")
    run.event("drafts-done")


def read_draft(run, name):
    path = run.room / "drafts" / f"{name}.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return f"({display(name)} wrote no draft file at {path})"


def phase_define(run):
    run.data["phase"] = "define"
    run.save()
    run.event("phase", phase="define")
    speaker = CLAUDE_NAME
    last_message = None
    agreed = {CLAUDE_NAME: False, CODEX_NAME: False}
    first = {CLAUDE_NAME: True, CODEX_NAME: True}
    while True:
        prompt = define_prompt(run, speaker, read_draft(run, other(speaker)), last_message, first[speaker])
        first[speaker] = False
        reply, status, _ = take_turn(run, speaker, "define", prompt)
        agreed[speaker] = status == "agreed"
        if status != "agreed":
            agreed[other(speaker)] = False
        if all(agreed.values()):
            break
        last_message = reply
        speaker = other(speaker)
    commit_room(run, "docs(pair-debate): record the definition of done")
    run.data["phase"] = "awaiting-approval"
    run.save()
    run.event("checkpoint", file=str(run.room / "definition-of-done.md"))


def phase_work(run, note):
    run.data["phase"] = "work"
    run.save()
    run.event("phase", phase="work")
    speaker = run.data.get("next_speaker", CLAUDE_NAME)
    last_message = run.data.get("last_message")
    agreed = {CLAUDE_NAME: False, CODEX_NAME: False}
    first = {CLAUDE_NAME: True, CODEX_NAME: True}
    check_passed = run.data.get("check_passed", False)
    while True:
        prompt = work_prompt(run, speaker, last_message, note if first[speaker] else None, first[speaker])
        first[speaker] = False
        reply, status, check = take_turn(run, speaker, "work", prompt)
        if check == "pass" and not check_passed:
            check_passed = True
            run.data["check_passed"] = True
            run.event("check-first-pass", who=display(speaker), turn=run.data["turn"])
        agreed[speaker] = status == "agreed"
        if status != "agreed":
            agreed[other(speaker)] = False
        run.data["last_message"] = reply
        run.data["next_speaker"] = other(speaker)
        run.save()
        if all(agreed.values()):
            break
        last_message = reply
        speaker = other(speaker)
    commit_room(run, "docs(pair-debate): close the transcript")
    run.data["phase"] = "done"
    run.save()
    run.event("agreed", branch=run.data["branch"], worktree=str(run.worktree), check=str(run.room / "check.sh"))


# ------------------------------------------------------------ commands ---


def ensure_tools():
    missing = [t for t in ("claude", "codex", "git") if shutil.which(t) is None]
    if missing:
        sys.exit("missing on PATH: " + ", ".join(missing))


def make_worktree(repo, topic):
    repo = Path(repo).resolve()
    branch = f"pair-debate/{topic}"
    path = repo.parent / f"{repo.name}-pair-debate-{topic}"
    if not path.exists():
        exists = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", branch],
            capture_output=True,
        ).returncode == 0
        cmd = ["git", "-C", str(repo), "worktree", "add", str(path)]
        cmd += [branch] if exists else ["-b", branch]
        subprocess.run(cmd, check=True)
    return path, branch


def cmd_start(args):
    ensure_tools()
    topic = re.sub(r"[^a-z0-9-]+", "-", args.topic.lower()).strip("-")
    state_dir = Path(args.state) if args.state else STATE_ROOT / topic
    run = Run(state_dir)
    if run.data.get("phase") not in (None, "error"):
        sys.exit(f"a run for {topic} is already in phase {run.data['phase']}; use resume or pick a new topic")
    brief = Path(args.brief).read_text(encoding="utf-8")
    worktree, branch = make_worktree(args.repo, topic)
    run.data.update({
        "topic": topic,
        "repo": str(Path(args.repo).resolve()),
        "worktree": str(worktree),
        "branch": branch,
        "out": args.out or f"docs/rooms/{topic}",
        "brief": str(Path(args.brief).resolve()),
        "turn": 0,
        "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    run.save()
    run.room.mkdir(parents=True, exist_ok=True)
    shutil.copy(args.brief, run.room / "brief.md")
    run.event("start", topic=topic, worktree=str(worktree), branch=branch, state=str(run.dir))
    phase_draft(run, brief)
    phase_define(run)


def cmd_resume(args):
    ensure_tools()
    run = Run(args.state)
    phase = run.data.get("phase")
    note = Path(args.note).read_text(encoding="utf-8") if args.note else None
    if phase == "awaiting-approval":
        phase_work(run, note)
    elif phase == "work":
        run.event("resume", phase="work")
        phase_work(run, note)
    elif phase == "error":
        sys.exit("the last turn failed; read events.jsonl, fix the cause, and start a new topic or edit state.json's phase by hand")
    else:
        sys.exit(f"nothing to resume from phase {phase}")


def cmd_status(args):
    run = Run(args.state)
    print(json.dumps(run.data, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--repo", required=True)
    start.add_argument("--topic", required=True)
    start.add_argument("--brief", required=True)
    start.add_argument("--out", help="room folder, relative to the worktree (default docs/rooms/<topic>)")
    start.add_argument("--state", help="state folder (default ~/.claude/gborges-standard/pair-debate/<topic>)")
    start.set_defaults(func=cmd_start)
    resume = sub.add_parser("resume")
    resume.add_argument("--state", required=True)
    resume.add_argument("--note", help="file holding the user's note to pass into the first work turn")
    resume.set_defaults(func=cmd_resume)
    status = sub.add_parser("status")
    status.add_argument("--state", required=True)
    status.set_defaults(func=cmd_status)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
