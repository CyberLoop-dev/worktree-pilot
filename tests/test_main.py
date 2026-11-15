import unittest
from main import parse_worktrees


class WorktreeParserTests(unittest.TestCase):
    def test_parses_attached_and_detached_worktrees(self):
        sample = "worktree /repo\nHEAD abc123\nbranch refs/heads/main\n\nworktree /tmp/demo\nHEAD def456\ndetached\n\n"
        result = parse_worktrees(sample)
        self.assertEqual(result[0]["branch"], "main")
        self.assertEqual(result[1]["branch"], "(detached)")
        self.assertEqual(result[1]["path"], "/tmp/demo")


if __name__ == "__main__":
    unittest.main()
