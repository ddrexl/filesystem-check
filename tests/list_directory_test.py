import os
import unittest

from filesystem_check.list_directory import list_sub_directory

this_dir = os.path.dirname(os.path.realpath(__file__))
example_directory = 'example_directory'


class TestListDirectory(unittest.TestCase):
    def test_example_directory(self):
        elements = list_sub_directory(this_dir, example_directory)

        self.assertSetEqual(set(elements), {
            '/.hidden',
            '/.hidden_dir',
            '/.hidden_dir/file',
            '/__dir',
            '/__dir/file',
            '/_dir',
            '/_dir/file',
            '/dir',
            '/dir/.hidden_dir',
            '/dir/.hidden_dir/.hidden',
            '/dir/.hidden_dir/file',
            '/dir/file',
            '/dir/nested',
            '/dir/nested/.hidden',
            '/dir/nested/file',
            '/file',
            '/file.txt',
        })
