from setuptools import setup
import ast
import os

def version():
    """Return version string."""
    with open(os.path.join('curtsies', '__init__.py')) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s

setup(name='curtsies',
      version=version(),
      description='Curses-like terminal wrapper, with colored strings!',
      url='https://github.com/thomasballinger/curtsies',
      author='Thomas Ballinger',
      author_email='thomasballinger@gmail.com',
      license='MIT',
      packages=['curtsies'],
      install_requires = [
          'blessings>=1.5',
          'wcwidth>=0.1.4',
      ],
      tests_require = [
          'mock',
          'pyte',
          'bpython',
          'nose',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      zip_safe=False)
