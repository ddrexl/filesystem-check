import inspect
from collections import defaultdict


class FilesystemChecksBase(object):
    """
    Subclass Example:

    class Subclass(FilesystemChecksBase):
        def __init__(self, paths):
            super().__init__(self, paths)

        def check_positive(self, path):
            if path is ok:
                return True     # True means match

        def check_negative(self, path):
            if path is not ok:
                self.set_error(path, 'path is not ok')
                return True
    """

    def __init__(self, derived, paths):
        self.paths = paths
        self.errors = defaultdict(str)
        self.checks = [method for name, method in inspect.getmembers(
            derived, predicate=inspect.isroutine) if name.startswith('check')]

    def run(self):
        for path in self.paths:
            for check in self.checks:
                match = check(path)
                if match:
                    break
            else:
                self.set_error(path, 'path not allowed')

    def get_error(self, path):
        return self.errors[path]

    def set_error(self, path, message):
        self.errors[path] = message

    def get_errors(self):
        errors = ((path, self.get_error(path)) for path in self.paths)
        formatting = '\n    Error: '
        error_lines = (path + formatting + error for path,
                       error in errors if error)
        return '\n'.join(error_lines)
