from setuptools import setup
import ast
import os


def version():
    """Return version string."""
    with open(os.path.join("curtsies", "__init__.py")) as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s


setup(
    version=version(),
)
