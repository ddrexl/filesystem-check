import unittest

from filesystem_check.aas_checks import AasChecks


class TestAasChecks(unittest.TestCase):
    def test_valid_paths(self):
        self.expect_valid([
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
        ])

    def test_non_snake_case_subdirectories(self):
        self.expect_error_message(
            'directory name must be snake_case', [
                '/communication/Some_type',
                '/communication/SomeType',
                '/communication/someType',
                '/communication/some_Type',
                '/communication/BUILD',     # this is ugly
            ])

    def test_path_not_allowed(self):
        self.expect_error_message('path not allowed', [
            '/lifecylce',
            '/lifecycle2',
            '/lifecycle2/foo',
            '/foo/some_type/some_type_conversion.cpp',
            '/unknown',
            '/some_file.cpp',
            '/some/nested/file.cpp',
        ])

    def test_invalid_source_file(self):
        self.expect_error_message('source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)', [
            '/communication/some_type/some_Type_conversion.cpp',
            '/communication/some_type/some_type_conversion2.cpp',
            '/communication/some_type/some_type_conversion.cxx',
            '/communication/some_type/SomeType.cpp',
        ])

    def expect_valid(self, example_paths):
        self.expect_error_message('', example_paths)

    def expect_error_message(self, message, example_paths):
        aas_checks = AasChecks(example_paths)
        aas_checks.run()
        for path in example_paths:
            error = aas_checks.get_error(path)
            self.assertEqual(message, error,
                             '{path} should {what}'.format(path=path, what='give error: ' + message if message else 'be valid'))

    def test_get_errors(self):
        aas_checks = AasChecks([
            '/foo',
            '/communication',
            '/communication/some_type',
            '/communication/some_type/some_type_codec.h',
            '/communication/SomeType',
            '/communication/SomeType/Codec.cpp',
        ])
        aas_checks.run()

        self.assertEqual("""/foo
    Error: path not allowed
/communication/SomeType
    Error: directory name must be snake_case
/communication/SomeType/Codec.cpp
    Error: source files must be either <type>_codec.(h|cpp) or <type>_conversion.(h|cpp)""", aas_checks.get_errors())
