import contextlib
import unittest
import sys
import warnings


class TestCase(unittest.TestCase):
    if sys.version_info[0] <= 2:

        @contextlib.contextmanager
        def subTest(self, **kwargs):
            yield

        def assertCountEqual(self, a, b):
            import collections

            self.assertEqual(
                collections.Counter(a),
                collections.Counter(b),
            )


@contextlib.contextmanager
def expect_warning(*messages):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        yield
        actual = {str(warning.message) for warning in w}
        assert actual == set(messages), "{actual!r} should match {expected!r}".format(
            actual=actual,
            expected=set(messages),
        )


WARN_SIMPLESPEC_MANY = "Passing 2+ arguments to SimpleSpec will be removed in 3.0; concatenate them with ',' instead."
WARN_SPECITEM = "The `SpecItem` class will be removed in 3.0."
WARN_SPEC_CLASS = "The Spec() class will be removed in 3.1; use SimpleSpec() instead."
WARN_SPEC_ITER = "Iterating over the components of a SimpleSpec object will be removed in 3.0."
WARN_SPEC_PARTIAL = "Partial versions will be removed in 3.0; use SimpleSpec('1.x.x') instead."
WARN_VERSION_PARTIAL = "Use of `partial=True` will be removed in 3.0."
