"""Minimal test suite for linestats CLI (stdlib only, unittest).

Run from repo root:
  python3 -m unittest discover -s tests -v
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parent.parent / "linestats.py"


def run_cli(args, stdin_text=None):
    """Run CLI, return (returncode, stdout, stderr). Path-independent."""
    return subprocess.run(
        [sys.executable, str(CLI)] + args,
        input=stdin_text,
        capture_output=True,
        text=True,
    )


def run_stdin(text, args=None):
    return run_cli(list(args or []), stdin_text=text)


def run_file(text, args=None):
    """Write text to a tempfile, run CLI against it."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(text)
        path = f.name
    try:
        return run_cli(list(args or []) + [path])
    finally:
        Path(path).unlink(missing_ok=True)


class TestEmptyInput(unittest.TestCase):
    def test_empty_stdin_human_zeros(self):
        p = run_stdin("")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(
            p.stdout,
            "total lines: 0\nnonempty lines: 0\nunique words: 0\nlongest line: 0\n",
        )

    def test_empty_stdin_json_zeros_and_longest_zero(self):
        p = run_stdin("", ["--json"])
        self.assertEqual(p.returncode, 0)
        self.assertEqual(
            json.loads(p.stdout),
            {"total_lines": 0, "nonempty_lines": 0,
             "unique_words": 0, "longest_line": 0},
        )


class TestBlankLines(unittest.TestCase):
    def test_blank_and_whitespace_only_not_counted(self):
        text = "a\n\n  \nB\n"
        p = run_stdin(text, ["--json"])
        self.assertEqual(p.returncode, 0)
        self.assertEqual(
            json.loads(p.stdout),
            {"total_lines": 4, "nonempty_lines": 2,
             "unique_words": 2, "longest_line": 3},
        )


class TestWordDedup(unittest.TestCase):
    def test_case_insensitive_punctuation_stripped(self):
        text = "Hello, hello! HELLO... world? 'World' (world)\n"
        p = run_stdin(text, ["--json"])
        self.assertEqual(json.loads(p.stdout)["unique_words"], 2)

    def test_punct_only_yields_zero_words(self):
        p = run_stdin("!!! ??? ...\n,;:\n", ["--json"])
        self.assertEqual(json.loads(p.stdout)["unique_words"], 0)

    def test_unicode_dedup(self):
        p = run_stdin("caf\u00e9 CAF\u00c9, na\u00efve!\n", ["--json"])
        self.assertEqual(json.loads(p.stdout)["unique_words"], 2)


class TestLongestLine(unittest.TestCase):
    def test_tie_first_wins(self):
        p = run_stdin("ab\ncd\nef\n", ["--json"])
        self.assertEqual(json.loads(p.stdout)["longest_line"], 1)

    def test_empty_zero(self):
        p = run_stdin("", ["--json"])
        self.assertEqual(json.loads(p.stdout)["longest_line"], 0)

    def test_later_longer_wins(self):
        p = run_stdin("a\nabcd\nab\n", ["--json"])
        self.assertEqual(json.loads(p.stdout)["longest_line"], 2)


class TestFileVsStdin(unittest.TestCase):
    def test_file_and_stdin_equivalence(self):
        text = "foo Bar\nbaz\n"
        via_stdin = run_stdin(text, ["--json"])
        via_file = run_file(text, ["--json"])
        self.assertEqual(via_stdin.returncode, 0)
        self.assertEqual(via_file.returncode, 0)
        self.assertEqual(
            json.loads(via_stdin.stdout), json.loads(via_file.stdout)
        )
        self.assertEqual(
            json.loads(via_file.stdout),
            {"total_lines": 2, "nonempty_lines": 2,
             "unique_words": 3, "longest_line": 1},
        )


class TestJsonShape(unittest.TestCase):
    def test_json_keys_match_human_output(self):
        text = "foo Bar\n\nbaz qux\n"
        human = run_stdin(text)
        js = run_stdin(text, ["--json"])
        self.assertEqual(human.returncode, 0)
        self.assertEqual(js.returncode, 0)
        stats = json.loads(js.stdout)
        self.assertEqual(
            set(stats.keys()),
            {"total_lines", "nonempty_lines", "unique_words", "longest_line"},
        )
        lines = {}
        for line in human.stdout.strip().splitlines():
            key, _, val = line.partition(":")
            lines[key.strip()] = int(val.strip())
        self.assertEqual(lines["total lines"], stats["total_lines"])
        self.assertEqual(lines["nonempty lines"], stats["nonempty_lines"])
        self.assertEqual(lines["unique words"], stats["unique_words"])
        self.assertEqual(lines["longest line"], stats["longest_line"])


class TestErrors(unittest.TestCase):
    def test_missing_file_nonzero_and_stderr(self):
        p = run_cli(["/nonexistent-file-xyz"])
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(p.returncode, 1)
        self.assertIn("No such file", p.stderr)


if __name__ == "__main__":
    unittest.main()
