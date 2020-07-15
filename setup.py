from setuptools import setup
import ast
import os
import io


def version():
    """Return version string."""
    with open(os.path.join("curtsies", "__init__.py")) as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s


setup(
    name="curtsies",
    version=version(),
    description="Curses-like terminal wrapper, with colored strings!",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bpython/curtsies",
    author="Thomas Ballinger",
    author_email="thomasballinger@gmail.com",
    license="MIT",
    packages=["curtsies"],
    install_requires=[
        "blessings>=1.5",
        "wcwidth>=0.1.4",
        'typing; python_version<"3.5"',
    ],
    tests_require=["mock", "pyte", "nose",],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
)
