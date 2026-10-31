"""Private Git publishing must not create a public Cloudflare preview."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PrivateBranchTests(unittest.TestCase):
    def test_cloudflare_refuses_private_branch_before_building(self):
        environment = dict(os.environ, CF_PAGES='1', CF_PAGES_BRANCH='codex/private-blog')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')],
                                env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('disabled for the private blog branch', result.stderr)

    def test_editor_targets_private_branch(self):
        config = (ROOT / 'static/admin/config.yml').read_text()
        self.assertIn('  branch: codex/private-blog\n', config)


if __name__ == '__main__':
    unittest.main()
