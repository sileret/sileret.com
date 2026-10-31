"""The publisher must preserve the served release when a build or update fails."""
import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'deploy/vm/publish.py'
spec = importlib.util.spec_from_file_location('vm_publish', MODULE)
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class PublishSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / 'source'
        self.source.mkdir()
        self.previous = self.root / 'releases/previous'
        self.previous.mkdir(parents=True)
        (self.previous / 'index.html').write_text('Existing site')
        (self.root / 'current').symlink_to(self.previous)
        self.revision = 'a' * 40
        self.builds = 0
        for name, value in [('ROOT', self.root), ('SOURCE', self.source), ('LOCK', self.root / 'publish.lock')]:
            context = patch.object(publisher, name, value)
            context.start()
            self.addCleanup(context.stop)
        context = patch.dict(os.environ)
        context.start()
        self.addCleanup(context.stop)

    def command(self, *args, **kwargs):
        if args[:2] == ('git', 'rev-parse'):
            return SimpleNamespace(stdout=self.revision)
        if args[:2] == ('python3', 'scripts/build.py'):
            self.builds += 1
            release = Path(args[-1])
            (release / 'index.html').write_text('Updated site')
            (release / 'pagefind').mkdir()
            (release / 'pagefind/pagefind.js').write_text('search')
        return SimpleNamespace(stdout='')

    def test_failed_build_keeps_previous_site(self):
        def fail(*args, **kwargs):
            if args[:2] == ('python3', 'scripts/build.py'):
                raise subprocess.CalledProcessError(1, args)
            return self.command(*args, **kwargs)
        with patch.object(publisher, 'run', side_effect=fail):
            with self.assertRaises(subprocess.CalledProcessError):
                publisher.main()
        self.assertEqual((self.root / 'current').resolve(), self.previous)
        self.assertEqual((self.root / 'current/index.html').read_text(), 'Existing site')
        self.assertEqual(list((self.root / 'releases').iterdir()), [self.previous])

    def test_success_publishes_complete_release_and_skips_same_revision(self):
        with patch.object(publisher, 'run', side_effect=self.command) as commands:
            publisher.main()
            self.assertTrue(any(call.args == ('git', 'fetch', '--prune', 'origin', publisher.BRANCH)
                                for call in commands.call_args_list))
            published = (self.root / 'current').resolve()
            self.assertNotEqual(published, self.previous)
            self.assertEqual((published / 'index.html').read_text(), 'Updated site')
            self.assertEqual((published / '.revision').read_text().strip(), self.revision)
            self.assertTrue((published / 'pagefind/pagefind.js').exists())
            publisher.main()
        self.assertEqual(self.builds, 1)
        self.assertTrue(self.previous.exists())

    def test_divergent_source_does_not_replace_site(self):
        def fail(*args, **kwargs):
            if args[:2] == ('git', 'merge'):
                raise subprocess.CalledProcessError(1, args)
            return self.command(*args, **kwargs)
        with patch.object(publisher, 'run', side_effect=fail):
            with self.assertRaises(subprocess.CalledProcessError):
                publisher.main()
        self.assertEqual((self.root / 'current').resolve(), self.previous)
        self.assertEqual(self.builds, 0)


if __name__ == '__main__':
    unittest.main()
