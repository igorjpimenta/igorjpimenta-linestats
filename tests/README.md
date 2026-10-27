# Tests

Minimal stdlib-only suite for the `linestats` CLI.

## Run

From the repo root:

```sh
python3 -m unittest discover -s tests -v
```

Requires Python 3.8+; no third-party dependencies.

## Covers

- empty stdin (human + json zeros, longest = 0)
- blank / whitespace-only lines excluded from nonempty count
- word dedup: case-insensitive, punctuation stripped, unicode, punct-only
- longest line: tie first-wins, empty zero, later-longer wins
- file vs stdin equivalence (tempfile, path-independent)
- json keys match human output values
- missing file exits nonzero with stderr
