#!/usr/bin/env python3
"""linestats - small portable line statistics CLI (stdlib only)."""
import json
import string
import sys

PUNCT = string.punctuation


def compute_stats(text):
    lines = text.splitlines()
    total = len(lines)
    nonempty = sum(1 for ln in lines if ln.strip() != "")
    words = set()
    for ln in lines:
        for tok in ln.split():
            w = tok.strip(PUNCT).lower()
            # also strip internal-adjacent leftovers like quotes inside?
            # strip any remaining leading/trailing punctuation
            w = w.strip(PUNCT)
            if w:
                words.add(w)
    longest = 0
    best_len = -1
    for i, ln in enumerate(lines, start=1):
        ln_len = len(ln)
        if ln_len > best_len:
            best_len = ln_len
            longest = i
    if total == 0:
        longest = 0
    return {
        "total_lines": total,
        "nonempty_lines": nonempty,
        "unique_words": len(words),
        "longest_line": longest,
    }


def print_human(stats, out):
    out.write(f"total lines: {stats['total_lines']}\n")
    out.write(f"nonempty lines: {stats['nonempty_lines']}\n")
    out.write(f"unique words: {stats['unique_words']}\n")
    out.write(f"longest line: {stats['longest_line']}\n")


def print_help(out):
    out.write("Usage: linestats [--json] [FILE...]\n")
    out.write("Report line stats. Reads FILE args if given, else stdin.\n")
    out.write("Options:\n")
    out.write("  --json, -j     output JSON object\n")
    out.write("  -h, --help     show this help\n")


def main(argv):
    args = list(argv[1:])
    as_json = False
    files = []
    for a in args:
        if a in ("--json", "-j"):
            as_json = True
        elif a in ("-h", "--help"):
            print_help(sys.stdout)
            return 0
        elif a == "--":
            # everything after -- is a file, but we already consumed;
            # treat remaining as files (simple: ignore marker)
            continue
        elif a.startswith("-") and a != "-":
            sys.stderr.write(f"linestats: unknown option: {a}\n")
            return 2
        else:
            files.append(a)

    if not files:
        # stdin mode ("-" also means stdin explicitly)
        text = sys.stdin.read()
    else:
        parts = []
        for path in files:
            if path == "-":
                parts.append(sys.stdin.read())
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    parts.append(f.read())
            except FileNotFoundError:
                sys.stderr.write(f"linestats: {path}: No such file or directory\n")
                return 1
            except IsADirectoryError:
                sys.stderr.write(f"linestats: {path}: Is a directory\n")
                return 1
            except OSError as e:
                sys.stderr.write(f"linestats: {path}: {e.strerror or e}\n")
                return 1
        text = "".join(
            p if p.endswith("\n") or p == "" else p + "\n" for p in parts
        )

    stats = compute_stats(text)
    if as_json:
        sys.stdout.write(json.dumps(stats) + "\n")
    else:
        print_human(stats, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
