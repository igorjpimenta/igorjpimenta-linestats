# linestats

Small, portable line-statistics CLI. Python 3 standard library only — no
dependencies, no install step beyond having `python3` on your `PATH`.

## Install

```console
$ git clone https://github.com/igorjpimenta/igorjpimenta-linestats
```

Run it directly:

```console
$ python3 igorjpimenta-linestats/linestats.py --help
Usage: linestats [--json] [FILE...]
Report line stats. Reads FILE args if given, else stdin.
Options:
  --json, -j     output JSON object
  -h, --help     show this help
```

(Or copy `linestats.py` anywhere on your `PATH` and drop the `.py`, since
the file is executable and has a shebang.)

## Usage

```
linestats [--json|-j] [FILE...]
```

- **No file arguments** — reads from **stdin**, so you can pipe into it.
- **One or more file arguments** — reads each file and reports stats for
  all of their contents combined.
- A file argument of `-` reads stdin at that position.
- `--json` (or `-j`) switches output to a single JSON object; without it
  the output is human-readable text.

## Metrics

| Field           | Meaning                                                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `total lines`   | Number of input lines (`\n`-terminated).                                                                                                   |
| `nonempty lines`| Lines with at least one non-whitespace character.                                                                                          |
| `unique words`  | Count of distinct words, lowercased, with leading/trailing punctuation stripped (`"two",` → `two`; `WORLD` and `world` are the same word). |
| `longest line`  | One-indexed number of the longest line; first wins on ties; `0` for empty input.                                                            |

In `--json` mode the same values appear as the keys `total_lines`,
`nonempty_lines`, `unique_words`, `longest_line`.

## Examples

Pipe from stdin:

```console
$ printf 'Hello world\nbye WORLD\n' | python3 linestats.py
total lines: 2
nonempty lines: 2
unique words: 3
longest line: 1
```

(`Hello`, `world`, `bye` — `world` appears twice but is case-insensitive,
so three unique words; the longest line is `Hello world`, which is line 1
with 11 characters, versus `bye WORLD` with 9.)

JSON output with a file argument:

```console
$ printf 'alpha beta\n  gamma,beta.\n' > sample.txt
$ python3 linestats.py --json sample.txt
{"total_lines": 2, "nonempty_lines": 2, "unique_words": 3, "longest_line": 2}
```

(Alpha, beta, gamma — beta repeats, so three unique words; the longest
line is line 2 with 13 characters, versus line 1 with 10.)

## Exit codes

| Code | Meaning                                                |
| ---- | ------------------------------------------------------ |
| `0`  | Success (including empty input, which reports all zeros and `longest line: 0`). |
| `1`  | A file argument that doesn't exist (or is a directory / unreadable) — message on stderr, no stdout. |
| `2`  | Unknown option passed on the command line.              |
