"""Define metadata for DataEnum."""

# Third Party
from pathlib import Path

import setuptools

long_description = Path("README.md").read_text()

setuptools.setup(
    name="data-enum",
    version="2.1.0",
    author="Chase Finch",
    author_email="chase@finch.email",
    description="An alternative to the built-in Python `enum` implementation",
    keywords=["Enum", "Enumeration"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chasefinch/data-enum",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[],
)
