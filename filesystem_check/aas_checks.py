import re
import inspect
from collections import defaultdict


class AasChecks(object):
    def __init__(self, paths):
        self.paths = paths
        self.errors = defaultdict(str)
        self.checks = [method for name, method in inspect.getmembers(
            AasChecks, predicate=inspect.isroutine) if name.startswith('check')]

    def run(self):
        for path in self.paths:
            for check in self.checks:
                match = check(self, path)
                if (match):
                    break
            else:
                self.set_error(path, 'path not allowed')

    def get_error(self, path):
        return self.errors[path]

    def set_error(self, path, message):
        self.errors[path] = message

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
            self.set_error(path, 'directory name must be snake_case')
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
            self.set_error(
                path, 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)')
            return True
        else:
            return False

    def check_communication_build_file(self, path):
        snake_case_pattern = r'[a-z0-9]+(_[a-z0-9]+)*'
        build_file = re.compile(
            r'^/communication/{snake_case}/BUILD$'.format(snake_case=snake_case_pattern))
        return build_file.match(path)
