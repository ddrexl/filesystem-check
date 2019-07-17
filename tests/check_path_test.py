import unittest


class AasChecks(object):
    def __init__(self, paths):
        self.paths = paths
        self.errors = []

    def run(self):
        for path in self.paths:
            error = self.check(path)
            if(error):
                self.errors.append(error)

    def get_errors(self):
        return '\n'.join(self.errors)

    def check(self, path):
        if path == '/communication':
            return ''
        return 'Unknown file'


class TestCheckPath(unittest.TestCase):
    def setUp(self):
        self.checks = AasChecks([])

        self.examples = {
            '/unknown': 'Unknown file',
            '/communication': '',
        }

    def test_examples(self):
        for path, error_message in self.examples.items():
            self.assertEqual(error_message, self.checks.check(path))
