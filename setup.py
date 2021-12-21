#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'skosprovider_sqlalchemy',
]

requires = [
    'skosprovider>=1.1.0',
    'sqlalchemy',
]

setup(
    name='skosprovider_sqlalchemy',
    version='1.0.0',
    description='A sqlAlchemy implementation of skosprovider.',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    author='Koen Van Daele',
    author_email='koen_van_daele@telenet.be',
    url='https://github.com/OnroerendErfgoed/skosprovider_sqlalchemy',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'skosprovider_sqlalchemy': 'skosprovider_sqlalchemy'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='nose.collector',
    entry_points="""\
    [console_scripts]
    init_skos_db = skosprovider_sqlalchemy.scripts.init_skos_db:main
    calc_visitation = skosprovider_sqlalchemy.scripts.calc_visitation:main
    """,
)
