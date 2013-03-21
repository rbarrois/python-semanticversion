#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois

from distutils.core import setup
from distutils import cmd
import os
import re
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version():
    version_re = re.compile(r"^__version__ = '([\w_.-]+)'$")
    with open(os.path.join(root_dir, 'src', 'semantic_version', '__init__.py')) as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.0.0'


class test(cmd.Command):
    """Run the tests for this package."""
    command_name = 'test'
    description = 'run the tests associated with the package'

    user_options = [
        ('test-suite=', None, "A test suite to run (defaults to 'tests')"),
    ]

    DEFAULT_TEST_SUITE = 'tests'

    def initialize_options(self):
        self.test_runner = None
        self.test_suite = None

    def finalize_options(self):
        self.ensure_string('test_suite', self.DEFAULT_TEST_SUITE)

    def run(self):
        """Run the test suite."""
        try:
            import unittest2 as unittest
        except ImportError:
            import unittest

        if self.verbose:
            verbosity=1
        else:
            verbosity=0

        ex_path = sys.path
        sys.path.insert(0, os.path.join(root_dir, 'src'))
        loader = unittest.defaultTestLoader
        suite = unittest.TestSuite()

        if self.test_suite == self.DEFAULT_TEST_SUITE:
            for test_module in loader.discover('.'):
                suite.addTest(test_module)
        else:
            suite.addTest(loader.loadTestsFromName(self.test_suite))

        result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
        sys.path = ex_path

        if not result.wasSuccessful():
            sys.exit(1)


setup(
    name="semantic_version",
    version=get_version(),
    author="Raphaël Barrois",
    author_email="raphael.barrois+semver@polytechnique.org",
    description=("A library implementing the 'SemVer' scheme."),
    license="BSD",
    keywords=['semantic version', 'versioning', 'version'],
    url="http://github.com/rbarrois/python-semanticversion",
    download_url="http://pypi.python.org/pypi/semantic_version/",
    package_dir={'': 'src'},
    packages=['semantic_version'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'test': test},
)

