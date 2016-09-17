#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import codecs
import os
import re
import sys

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `__init__.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('gargoyle')


if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("rm -rf .eggs/ build/ dist/")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a v%s -m 'Version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

with codecs.open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with codecs.open('HISTORY.rst', 'r', encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='gargoyle-yplan',
    version=version,
    author='DISQUS',
    author_email='opensource@disqus.com',
    maintainer='YPlan',
    maintainer_email='adam@yplanapp.com',
    url='https://github.com/YPlan/gargoyle',
    description=(
        'Gargoyle is a platform built on top of Django which allows you to switch functionality of your application '
        'on and off based on conditions.'
    ),
    long_description=readme + '\n\n' + history,
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    install_requires=[
        'django-modeldict-yplan>=1.5.0',
        'nexus-yplan>=1.2.0',
        'django-jsonfield>=0.9.2,!=0.9.13,!=1.0.0',
    ],
    extras_require={
        ':python_version=="2.7"': [
            'contextdecorator',
        ]
    },
    license='Apache License 2.0',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],
)
