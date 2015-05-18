#!/usr/bin/env python

from distutils.core import setup, Command


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
        

setup(name='ghdecoy',
      version='0.1.0',
      description='Populate your github contribution graph',
      author='tickelton',
      author_email='tickelton@gmail.com',
      url='https://github.com/tickelton/ghdecoy',
      license='ISC',
      scripts=['ghdecoy.py'],
      cmdclass = {'test': RunTests},
      )
