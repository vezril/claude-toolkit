"""Parse access-log lines: "<ip> <method> <path> <status> <ms>"."""


def parse_line(line):
    ip, method, path, status, ms = line.split()
    return (ip, method, path, int(status), int(ms))


def parse_log(text):
    """Records in order of first appearance, duplicates dropped."""
    out = []
    seen = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        rec = parse_line(line)
        if rec not in seen:
            seen.add(rec)
            out.append(rec)
    return out
