#!/usr/bin/python
import optparse
import sys
from subprocess import call
# Install the Python unittest2 package before you run this script.
import unittest


USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_paths=()):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()

    full_suite = unittest.TestSuite()
    for item in test_paths:
        full_suite.addTest(unittest.loader.TestLoader().discover(item))

    unittest.TextTestRunner(verbosity=2).run(full_suite)

def js_test():
    path = './views/scripts/tests/'
    script_name = 'lib/phantom-jasmine/run-jasmine-test.coffee'
    page_name = 'SpecRunner.html'

    call(['phantomjs', path+script_name, path+page_name])

if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) != 2:
        # Default arguments
        SDK_PATH = args[0] if len(args) > 0 else '/usr/local/bin'
        TEST_PATHS = [
            './tests/unit',
            './tests/func'
        ]
    else:
        SDK_PATH = args[0]
        TEST_PATH = args[1]
    main(SDK_PATH, TEST_PATHS)
    #js_test()
