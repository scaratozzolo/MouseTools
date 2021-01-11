import setuptools
from MouseTools.__init__ import __version__



with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MouseTools",
    version=__version__,
    author="Scott Caratozzolo",
    author_email="scaratozzolo12@gmail.com",
    description="A Python wrapper for the Disney API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scaratozzolo/MouseTools",
    packages=setuptools.find_packages(),
    package_data = {'MouseTools': ['MouseTools.db']},
    install_requires=["requests"],
    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
)
