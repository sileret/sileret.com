import importlib.util
import sys
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
