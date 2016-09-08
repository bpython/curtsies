from setuptools import setup
import ast
import os
import io

def version():
    """Return version string."""
    with open(os.path.join('curtsies', '__init__.py')) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s

def get_long_description():
    with io.open('readme.md', encoding="utf-8") as f:
        long_description = f.read()

    try:
        import pypandoc
    except ImportError:
        print('pypandoc not installed, using file contents.')
        return long_description

    try:
        long_description = pypandoc.convert('readme.md', 'rst')
    except OSError:
        print("Pandoc not found. Long_description conversion failure.")
        return long_description
    else:
        long_description = long_description.replace("\r", "")
    return long_description

setup(name='curtsies',
      version=version(),
      description='Curses-like terminal wrapper, with colored strings!',
      long_description=get_long_description(),
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
