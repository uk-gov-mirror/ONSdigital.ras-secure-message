import unittest
import os
import sys

if __name__ == "__main__":
    test_dirs = os.listdir('./tests')
    suites_list = []
    loader = unittest.TestLoader()
    for directory in test_dirs:
        test_path = "./tests/{}".format(directory)
        suite = loader.discover(test_path)
        suites_list.append(suite)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(result.failures)