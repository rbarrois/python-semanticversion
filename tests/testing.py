import unittest
import sys
import warnings


class TestCase(unittest.TestCase):
    if sys.version_info[0] <= 2:
        import contextlib

        @contextlib.contextmanager
        def subTest(self, **kwargs):
            yield

        def assertCountEqual(self, a, b):
            import collections

            self.assertEqual(
                collections.Counter(a),
                collections.Counter(b),
            )
