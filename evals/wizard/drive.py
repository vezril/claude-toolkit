"""Drive a wizard script the way a person would: in a pseudo-terminal, answering each
prompt as it appears. Usage: python3 drive.py <script> <repo> <y|n> <stubs> <log>
Prints JSON: exit code, transcript (what the terminal showed, echoes included), and
the answers given. Yes/no prompts get the mode's answer; counts get 42; any other
prompt gets a unique token (tok01, tok02, ...), except that an offered default
([example/pantry]) is kept with Enter, so where a value ends up, and whether
it was echoed, can be traced afterwards.
"""
import json, os, pty, re, select, signal, sys, time

script, repo, mode, stubs, log = sys.argv[1:6]
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b[()][A-Z0-9]|[\x00-\x08\x0b-\x1f]")
YESNO = re.compile(r"\[y/n\]|\(y/n\)|\by/n\b|\byes/no\b|\[yes/no\]", re.I)
VALUE = re.compile(r"paste|enter|type|name|url|dsn|key|token|secret|value|string|id\b|password|address|which|what", re.I)
COUNT = re.compile(r"how many|count|number of|rows", re.I)

TYPED = re.compile(r"""(?i:type)\s+(?:(?i:the [\w ]+? exactly)\s*:\s*(\S+)|['"‘“]([^'"’”]+)['"’”]|(.+?)\s+(?i:to (?:proceed|continue|confirm))|([A-Z][A-Z0-9_-]+)\b)""")
DEFAULT = re.compile(r"\[([^\]]+)\]\s*:?\s*$")

def answer(prompt, n):
    p = prompt.strip()
    t = TYPED.search(p)
    if t:
        return next(g for g in t.groups() if g).strip().rstrip("?:").strip() if mode == "y" else "no"
    d = DEFAULT.search(p)
    if d and not YESNO.search(p) and d.group(1).strip():
        return ""  # a person keeps the offered default with Enter
    if YESNO.search(p):
        return mode
    if COUNT.search(p):
        return "42"
    if p.endswith("?") and not VALUE.search(p):
        return mode
    if re.search(r"\bsk_", p):
        return f"sk_test_tok{n:02d}"
    if re.search(r"\bpk_", p):
        return f"pk_test_tok{n:02d}"
    if re.search(r"postgres|connection string|database url|database_url", p, re.I):
        return f"postgres://pantry:tok{n:02d}@db.example.test:5432/pantry"
    if re.search(r"https?://|url|dsn", p, re.I):
        return f"https://tok{n:02d}@example.test/1"
    return f"tok{n:02d}"

env = {**os.environ, "PATH": stubs + ":" + os.environ["PATH"], "WIZARD_LOG": log, "TERM": "xterm", "HOME": os.path.dirname(repo)}
pid, fd = pty.fork()
if pid == 0:
    os.chdir(repo)
    os.execvpe("bash", ["bash", script], env)

out = b""; mark = 0; answers = []; start = time.time(); quiet_since = time.time(); code = None; timed_out = False
while True:
    r, _, _ = select.select([fd], [], [], 0.1)
    if r:
        try:
            data = os.read(fd, 65536)
        except OSError:
            data = b""
        if data:
            out += data; quiet_since = time.time(); continue
    wp, status = os.waitpid(pid, os.WNOHANG)
    if wp:
        code = os.waitstatus_to_exitcode(status)
        try:
            while True:
                data = os.read(fd, 65536)
                if not data: break
                out += data
        except OSError:
            pass
        break
    if time.time() - start > 45 or len(answers) > 120:
        timed_out = True; os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0); break
    if time.time() - quiet_since > 0.35:
        text = ANSI.sub("", out[mark:].decode("utf8", "replace"))
        lines = [l for l in text.splitlines() if l.strip()]
        prompt = lines[-1] if lines else ""
        # A bare "? " or "> " prompt: the instruction is on the line above.
        if len(prompt.strip()) < 8 and len(lines) > 1:
            prompt = lines[-2] + " " + prompt
        if len(answers) >= 6 and all(a[0] == prompt for a in answers[-6:]):
            timed_out = True; os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0); break
        a = answer(prompt, len(answers) + 1)
        answers.append([prompt[-160:], a])
        os.write(fd, (a + "\n").encode())
        mark = len(out); quiet_since = time.time()

print(json.dumps({"code": code, "timedOut": timed_out, "transcript": ANSI.sub("", out.decode("utf8", "replace")), "answers": answers}))
