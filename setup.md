
## Set up for development
To set up a local repository to begin using curtsies as a developer, run

    $ git clone https://github.com/bpython/curtsies.git
    $ cd curtsies
    $ pip install -e .

## Running Tests
Tests are written using the unittest framework and are run using using [nosetests](https://nose.readthedocs.io/en/latest/). To run all tests, do:

    $ pip install pyte coverage mock nose
    $ nosetests .

## Style / Formatting
Since curtsies is most commonly used with [bpython](https://github.com/bpython), we adhere to bpython's style, which uses  the [black library](https://pypi.org/project/black) to auto-format.

To auto-format a modified file to curtsies' formatting specifications (which are specified in `pyproject.toml`), run

    $ pip install black
    $ black {source_file_or_directory}
    
## Migrating format changes without ruining git blame
So as to not pollute `git blame` history, for large reformatting or renaming commits, place the 40-character commit ID into the `.git-blame-ignore-revs` file underneath a comment describing the its contents.

Then, to see a clean and meaningful blame history of a file:

    $ git blame --ignore-revs-file .git-blame-ignore-revs <file>

You can also configure git (locally) to automatically ignore revision changes with every call to `git blame`:

    $ git config blame.ignoreRevsFile .git-blame-ignore-revs



