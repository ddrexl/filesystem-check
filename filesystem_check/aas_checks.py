import re

from filesystem_check.base import FilesystemChecksBase


class AasChecks(FilesystemChecksBase):
    def __init__(self, paths):
        super().__init__(self, paths)

        self.lifecycle_directory = re.compile(r'^/lifecycle(/.+)*$')
        self.communication_directory = re.compile(r'^/communication$')
        snake_case = r'[a-z0-9]+(_[a-z0-9]+)*'
        self.snake_sub_dir = re.compile(
            r'^/communication/{snake_case}$'.format(snake_case=snake_case))
        self.any_sub_dir = re.compile(r'^/communication/[^/]+$')
        self.source_files = re.compile(
            r'^/communication/(?P<independent_type>{snake_case})/(?P=independent_type)_(codec|conversion)\.(h|cpp)$'.format(snake_case=snake_case))
        self.any_files = re.compile(r'^/communication/.*/.*$')
        self.build_file = re.compile(
            r'^/communication/{snake_case}/BUILD$'.format(snake_case=snake_case))

    def check_lifecycle(self, path):
        return self.lifecycle_directory.match(path)

    def check_communication_directory(self, path):
        return self.communication_directory.match(path)

    def check_communication_subdirectory_is_snake_case(self, path):
        return self.snake_sub_dir.match(path)

    def check_communication_subdirectory_is_not_snake_case_error(self, path):
        if self.any_sub_dir.match(path) and not self.check_communication_subdirectory_is_snake_case(path):
            self.set_error(path, 'directory name must be snake_case')
            return True

    def check_communication_valid_source_file(self, path):
        return self.source_files.match(path)

    def check_communication_invalid_source_file(self, path):
        if self.any_files.match(path) and not self.check_communication_valid_source_file(path) and not self.check_communication_build_file(path):
            self.set_error(
                path, 'source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)')
            return True

    def check_communication_build_file(self, path):
        return self.build_file.match(path)
