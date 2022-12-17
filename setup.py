import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MouseTools",
    author="Scott Caratozzolo",
    author_email="scaratozzolo12@gmail.com",
    description="A Python wrapper for the Disney API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scaratozzolo/MouseTools",
    packages=setuptools.find_packages(),
    install_requires=[
            "requests",
            "pytz",
        ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
)
