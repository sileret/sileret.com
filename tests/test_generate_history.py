import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_history.py"
SPEC = importlib.util.spec_from_file_location("generate_history", SCRIPT_PATH)
generate_history = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = generate_history
SPEC.loader.exec_module(generate_history)


class GenerateHistoryTests(unittest.TestCase):
    def test_word_changes_preserve_both_versions_and_punctuation(self):
        before = "It costs €10, including tax.\nTry again."
        after = "It costs €12, excluding tax.\nTry again!"
        segments = generate_history.word_changes(before, after)
        self.assertEqual("".join(s["text"] for s in segments if s["kind"] != "insert"), before)
        self.assertEqual("".join(s["text"] for s in segments if s["kind"] != "delete"), after)
        self.assertIn({"kind": "delete", "text": "10"}, segments)
        self.assertIn({"kind": "insert", "text": "12"}, segments)

    def test_comparison_detects_title_and_content_changes(self):
        before = '---\ntitle: "Old title"\nlastmod: 2026-01-01\n---\n\nSame intro.\n\nA small cost.\n'
        after = '---\ntitle: "New title"\nlastmod: 2026-02-01\n---\n\nSame intro.\n\nA large cost.\n'
        changes = generate_history.comparison_changes(before, after)
        self.assertTrue(changes["has_content_changes"])
        self.assertEqual("".join(s["text"] for s in changes["title_changes"] if s["kind"] != "delete"), "New title")
        self.assertNotIn("lastmod", str(changes))

    def test_metadata_only_changes_have_no_text_diff(self):
        self.assertEqual(generate_history.comparison_changes(
            '---\ntitle: Example\nlastmod: 2026-01-01\n---\nBody.\n',
            '---\ntitle: Example\nlastmod: 2026-02-01\n---\nBody.\n',
        ), {"title_changes": [], "has_content_changes": False})

    def test_generate_compares_adjacent_committed_versions_across_rename(self):
        import json
        import subprocess

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            posts = root / "content" / "posts"
            post = posts / "old" / "index.md"
            post.parent.mkdir(parents=True)

            def git(*args):
                return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

            git("init", "-q")
            git("config", "user.name", "History Test")
            git("config", "user.email", "history@example.invalid")
            for text, subject in (("Original.", "Publish post"), ("Original.\n\nMore detail.", "Add detail")):
                post.write_text(f'---\ntitle: "Example"\n---\n\n{text}\n', encoding="utf-8")
                git("add", ".")
                git("commit", "-qm", subject)
            renamed = posts / "new"
            git("mv", str(post.parent), str(renamed))
            git("commit", "-qm", "Rename post")
            # An unpublished working-tree edit must never leak into comparisons.
            (renamed / "index.md").write_text("Unpublished secret.", encoding="utf-8")
            generated = root / "content" / "post-versions"
            data_path = root / "data" / "generated_post_history.json"
            with mock.patch.multiple(generate_history, ROOT=root, POSTS_DIR=posts,
                                     GENERATED_CONTENT_DIR=generated, GENERATED_DATA_PATH=data_path):
                history = generate_history.generate()
            entries = history["posts/new/index.md"]["versions"]
            self.assertEqual(len(entries), 3)
            self.assertEqual(entries[-1]["changes_url"], "")
            comparisons = [json.loads(path.read_text()) for path in generated.rglob("*-changes.md")]
            self.assertEqual(len(comparisons), 2)
            by_subject = {page["subject"]: page for page in comparisons}
            self.assertFalse(by_subject["Rename post"]["has_content_changes"])
            detail = by_subject["Add detail"]
            self.assertTrue(detail["has_content_changes"])
            self.assertEqual(detail["title_changes"], [])
            self.assertEqual(detail["previous_url"], entries[-1]["url"])
            self.assertEqual(detail["version_url"], entries[1]["url"])
            self.assertTrue((generated / history["posts/new/index.md"]["stable_id"] / entries[0]["short_commit"] / "index.md").exists())
            self.assertTrue(all("/posts/new/" in page["url"] for page in comparisons))
            self.assertNotIn("Unpublished secret", str(comparisons))

    def test_rendered_diff_handles_replacements_and_repeated_words(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable for the browser diff algorithm check")
        subprocess.run([node, "-e", r'''
const assert = require('node:assert/strict');
const { changedTokens } = require(process.argv[1]);
const cases = [
  [[], []], [[], ['new']], [['old'], []],
  [['a', ' ', 'small', ' ', 'cost'], ['a', ' ', 'large', ' ', 'cost']],
  [['a', 'b', 'a', 'b'], ['b', 'a', 'b', 'a']],
  [['same'], ['same']], [['é', '→'], ['é', '✓']],
];
// Exhaust short repeated-token inputs to catch ambiguous alignments.
const sequences = [[]];
for (let length = 1; length <= 4; length++) {
  for (let mask = 0; mask < 2 ** length; mask++) {
    sequences.push(Array.from({ length }, (_, i) => (mask >> i) & 1));
  }
}
for (const old of sequences) for (const updated of sequences) cases.push([old, updated]);
for (const [old, updated] of cases) {
  const { removed, added } = changedTokens(old, updated);
  assert.deepEqual(old.filter((_, i) => !removed.has(i)), updated.filter((_, i) => !added.has(i)));
  const lengths = Array.from({ length: old.length + 1 }, () => Array(updated.length + 1).fill(0));
  for (let i = 1; i <= old.length; i++) for (let j = 1; j <= updated.length; j++) {
    lengths[i][j] = old[i - 1] === updated[j - 1] ? lengths[i - 1][j - 1] + 1 : Math.max(lengths[i - 1][j], lengths[i][j - 1]);
  }
  assert.equal(removed.size + added.size, old.length + updated.length - 2 * lengths[old.length][updated.length]);
}
''', str(SCRIPT_PATH.parents[1] / "static" / "post-changes.js")], check=True, capture_output=True, text=True)

    def test_split_front_matter(self):
        metadata, body = generate_history.split_front_matter(
            '---\ntitle: "Example"\nformat: article\n---\n\nBody text.\n'
        )
        self.assertEqual(metadata["title"], "Example")
        self.assertEqual(metadata["format"], "article")
        self.assertEqual(body, "\nBody text.\n")

    def test_split_front_matter_leaves_plain_markdown_unchanged(self):
        metadata, body = generate_history.split_front_matter("Body only.\n")
        self.assertEqual(metadata, {})
        self.assertEqual(body, "Body only.\n")

    def test_revision_log_uses_new_path_for_a_rename(self):
        output = (
            f"{generate_history.COMMIT_MARKER}\n"
            "abc123\x1f2026-08-08T10:00:00+02:00\x1fRename post\n\n"
            "R100\tcontent/posts/old/index.md\tcontent/posts/new/index.md\n"
        )
        fake_git_result = types.SimpleNamespace(stdout=output)
        fake_exists_result = types.SimpleNamespace(returncode=0)
        with mock.patch.object(generate_history, "git", return_value=fake_git_result), mock.patch.object(
            generate_history.subprocess, "run", return_value=fake_exists_result
        ):
            revisions = generate_history.parse_revision_log("content/posts/new/index.md")

        self.assertEqual(len(revisions), 1)
        self.assertEqual(revisions[0].path, "content/posts/new/index.md")
        self.assertEqual(revisions[0].subject, "Rename post")


if __name__ == "__main__":
    unittest.main()
