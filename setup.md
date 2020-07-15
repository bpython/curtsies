# Development Setup
This is for contributing to Curtsies. If you are just using the Curtsies library, not contributing changes to it, then just install curtsies with `pip install curtsies` and you're off to the races!

## Set up for development
To set up a local repository and install the project in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#install-editable) so that other Python programs on your computer will import this local version you're editing, run

    $ git clone https://github.com/bpython/curtsies.git
    $ cd curtsies
    $ pip install -e .

## Running Tests
Tests are written using the unittest framework and are run using using [nosetests](https://nose.readthedocs.io/en/latest/). To run all tests, do:

    $ pip install pyte coverage mock nose
    $ nosetests .

## Style / Formatting
Since curtsies is most commonly used with [bpython](https://github.com/bpython), we adhere to bpython's style, which uses the [black library](https://pypi.org/project/black) to auto-format.

To auto-format a modified file to curtsies' formatting specifications (which are specified in `pyproject.toml`), run

    $ pip install black
    $ black {source_file_or_directory}

If you are working on VS code, follow these steps to auto format from inside VS code:
    1. Make sure the python extension is installed
    2. Then got to File → Preferences → Settings
    3. Search for “python.formatting.provider”
    4. Change it to 'black'
    5. Optional - Format onSave
        - Still in settings search for “editor.formatOnSave” and check the box
        - This will auto format your code whenever you save
    6. If you choose not to auto-format on save
        - Use Command+Shift+P (on Mac) or Ctrl+Shift+P (Windows and Linux) to open the command palette.
        - Type in Format Document and select it to run the auto-formatter

## Migrating format changes without ruining git blame
So as to not pollute `git blame` history, for large reformatting or renaming commits, place the 40-character commit ID into the `.git-blame-ignore-revs` file underneath a comment describing the its contents.

Then, to see a clean and meaningful blame history of a file:

    $ git blame --ignore-revs-file .git-blame-ignore-revs <file>

You can also configure git (locally) to automatically ignore revision changes with every call to `git blame`:

    $ git config blame.ignoreRevsFile .git-blame-ignore-revs


