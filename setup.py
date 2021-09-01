# -*- coding: UTF-8 -*-
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='data-enum',
    version='1.2.2',
    author='Chase Finch',
    author_email='chase@finch.email',
    description='An alternative to the built-in Python `enum` implementation',
    keywords=['Enum', 'Enumeration'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chasefinch/data-enum',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7',
    install_requires=[
        'future;python_version<="2.7"',
    ],
)
