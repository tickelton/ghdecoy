#!/usr/bin/env python

import os
from distutils.core import setup, Command
from distutils.command.install import install


class RunTests(Command):
    """Run the test suite."""

    description = 'run all tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        subprocess.call(['python', '-m', 'unittest', 'discover', '-v'])


class CoverageRun(Command):
    """Run coverage analysis."""

    description = 'run test coverage analysis'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        subprocess.call([
            'python-coverage',
            'run',
            '-m',
            'unittest',
            'discover',
            '-v'
        ])


class CoverageReport(Command):
    """Report results of coverage analysis."""

    description = 'report results of coverage analysis'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        subprocess.call(['python-coverage', 'report', '-m'])


class GHDInstall(install):

    user_options = install.user_options

    def initialize_options(self):
        install.initialize_options(self)

    def run(self):
        install.run(self)
        install.copy_tree(self, './man', os.path.join(self.prefix, 'man'))


setup(name='ghdecoy',
      version='0.3.0',
      description='Populate your github contribution graph',
      author='tickelton',
      author_email='tickelton@gmail.com',
      url='https://github.com/tickelton/ghdecoy',
      license='ISC',
      scripts=['ghdecoy.py'],
      cmdclass={
          'test': RunTests,
          'coverage_run': CoverageRun,
          'coverage_report': CoverageReport,
          'install': GHDInstall,
      },
      )
