import unittest

import re
import inspect
from collections import defaultdict


class AasChecks(object):
    def __init__(self, paths):
        self.paths = paths
        self.errors = defaultdict(list)
        self.checks = [method for name, method in inspect.getmembers(
            AasChecks, predicate=inspect.isroutine) if name.startswith('check')]

    def run(self):
        for path in self.paths:
            for check in self.checks:
                match = check(self, path)
                if (match):
                    break
            else:
                self.error(path, 'path not allowed')

    def get_errors_for_path(self, path):
        return self.errors[path]

    def error(self, path, message):
        self.errors[path].append(message)

    # def get_all_errors(self):
    #     def errors_for_path(path):
    #         return '\n'.join(['    ' + e for e in self.errors[path]])
    #     errors = ''
    #     for path in self.errors:
    #         errors += path + '\n' + errors_for_path(path)

    #     return errors

    def check_lifecycle(self, path):
        lifecycle = re.compile(r'^/lifecycle(/.+)*$')
        return lifecycle.match(path)

    def check_communication_directory(self, path):
        com_dir = re.compile(r'^/communication$')
        return com_dir.match(path)

    def check_communication_subdirectory_is_snake_case(self, path):
        snake_case_pattern = r'[a-z0-9]+(_[a-z0-9]+)*'
        snake_sub_dir = re.compile(
            r'^/communication/{snake_case}$'.format(snake_case=snake_case_pattern))
        return snake_sub_dir.match(path)

    def check_communication_subdirectory_is_not_snake_case_error(self, path):
        any_sub_dir = re.compile(r'^/communication/[^/]+$')
        if any_sub_dir.match(path) and not self.check_communication_subdirectory_is_snake_case(path):
            self.error(path, 'directory name must be snake_case')
            return True
        else:
            return False

    def check_communication_valid_source_file(self, path):
        snake_case_pattern = r'[a-z0-9]+(_[a-z0-9]+)*'
        source_files = re.compile(
            r'^/communication/(?P<independent_type>{snake_case})/(?P=independent_type)_(codec|conversion)\.(h|cpp)$'.format(snake_case=snake_case_pattern))
        return source_files.match(path)

    def check_communication_invalid_source_file(self, path):
        any_files = re.compile(r'^/communication/.*/.*$')
        if any_files.match(path) and not self.check_communication_valid_source_file(path) and not self.check_communication_build_file(path):
            self.error(
                path, 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)')
            return True
        else:
            return False

    def check_communication_build_file(self, path):
        snake_case_pattern = r'[a-z0-9]+(_[a-z0-9]+)*'
        build_file = re.compile(
            r'^/communication/{snake_case}/BUILD$'.format(snake_case=snake_case_pattern))
        return build_file.match(path)


class TestAasChecks(unittest.TestCase):
    def setUp(self):
        self.examples = {
            '/lifecylce': 'path not allowed',
            '/lifecycle2': 'path not allowed',
            '/lifecycle2/foo': 'path not allowed',
            '/communication/Some_type': 'directory name must be snake_case',
            '/communication/SomeType': 'directory name must be snake_case',
            '/communication/someType': 'directory name must be snake_case',
            '/communication/some_Type': 'directory name must be snake_case',
            '/communication/some_type/some_Type_conversion.cpp': 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)',
            '/communication/some_type/some_type_conversion2.cpp': 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)',
            '/communication/some_type/some_type_conversion.cxx': 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)',
            '/communication/some_type/SomeType.cpp': 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)',
            '/foo/some_type/some_type_conversion.cpp': 'path not allowed',
            '/unknown': 'path not allowed',
            '/some_file.cpp': 'path not allowed',
            '/some/nested/file.cpp': 'path not allowed',
        }

    def test_examples(self):
        for path, error_message in self.examples.items():
            aas_checks = AasChecks([path])
            aas_checks.run()
            errors = aas_checks.get_errors_for_path(path)

            if error_message:
                self.assertEqual([error_message], errors, '{0} should give error: {1}'.format(
                    path, error_message))

    def test_valid_paths(self):
        valid_paths = [
            '/lifecycle',
            '/lifecycle/anything',
            '/lifecycle/anything/below.txt',
            '/lifecycle/anything/.goes',
            '/communication',
            '/communication/some_type',
            '/communication/some_type1',
            '/communication/sometype',
            '/communication/sometype1',
            '/communication/some12_type',
            '/communication/1some_type',
            '/communication/some_type/some_type_codec.h',
            '/communication/some_type/some_type_codec.cpp',
            '/communication/some_type/some_type_conversion.h',
            '/communication/some_type/some_type_conversion.cpp',
            '/communication/some_type/BUILD',
            '/communication/some_other_type/some_other_type_codec.h',
            '/communication/some_other_type/some_other_type_codec.cpp',
            '/communication/some_other_type/BUILD',
        ]

        for path in valid_paths:
            aas_checks = AasChecks([path])
            aas_checks.run()
            errors = aas_checks.get_errors_for_path(path)

            self.assertEqual([], errors, '{0} should be valid'.format(path))

    def test_path_not_allowed(self):
        '''Not caught by any check, e.g. typos'''

        path_not_allowed = {
            '/lifecylce': 'path not allowed',
            '/lifecycle2': 'path not allowed',
            '/lifecycle2/foo': 'path not allowed',
            '/foo/some_type/some_type_conversion.cpp': 'path not allowed',
            '/unknown': 'path not allowed',
            '/some_file.cpp': 'path not allowed',
            '/some/nested/file.cpp': 'path not allowed',
        }

        for path, error_message in path_not_allowed.items():
            aas_checks = AasChecks([path])
            aas_checks.run()
            errors = aas_checks.get_errors_for_path(path)

            self.assertEqual(['path not allowed'], errors,
                             '{0} should give error: {1}'.format(path, error_message))
