## Set up for development
To set up a local repository to begin using curtsies as a developer, run

    $ git clone https://github.com/bpython/curtsies.git
    $ cd curtsies
    $ pip install -e .

## Running Tests
--------
Tests are written using the unittest framework and are run using using [pyte](https://pypi.org/project/pyte/), [coverage](https://coverage.readthedocs.io/en/coverage-5.1/),  [mock](https://pypi.org/project/mock/), and [nosetests](https://nose.readthedocs.io/en/latest/). To run all tests, do:

    $ pip install pyte coverage mock nose
    $ nosetests .

Curtsies builds/pull requests are automatically tested on [Travis Ci](https://travis-ci.org/github/bpython/curtsies) following uploads, although we have ran into cases where tests pass locally but not on Travis CI. If this happens to you, be sure to document it.

## Style / Formatting
--------
Since curtsies is most commonly used with [bpython](https://github.com/bpython), we adhere to bpython's style, which uses  the [black library](https://pypi.org/project/black) to auto-format.

To auto-format a modified file to curtsies' formatting specifications (which are specified in `pyproject.toml`), run

    $ pip install black
    $ black {source_file_or_directory} p