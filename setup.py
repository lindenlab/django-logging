import os
import re
from setuptools import setup, find_packages


def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
        return readme.read()


def version():
    _changename = os.path.join(os.path.dirname(__file__),
                               "debian", "changelog")
    try:
        _changelog = open(_changename)
        _firstline = _changelog.readline()
        _changelog.close()
    except IOError as _err:
        raise ConfError("Can't read debian changelog file at %s: %s" %
                        (_changename, _err))

    # e.g. "llbase (0.7) unstable; urgency=medium"
    # find just the parenthesized, dotted-decimal version number
    _match = re.search(r"\(([0-9]+(\.[0-9]+)+)", _firstline)
    if not _match:
        raise ConfError("First line of %s does not contain (version)" %
                        _changename)

    # The short X.Y version.
    version = _match.group(1)
    # The full version, including alpha/beta/rc tags.
    release = version

    return release


setup(
    name='python-django-logging-middleware-linden',
    version=version(),
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    description='A simple Django app to log requests/responses in various formats, such as JSON.',
    long_description=readme(),
    url='https://github.com/lindenlab/django-logging',
    author='Log Linden',
    author_email='log@lindenlab.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Framework :: Django",
        "Framework :: Django :: 1.4",
        "Framework :: Django :: 1.5",
        "Framework :: Django :: 1.6",
        "Framework :: Django :: 1.7",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
    ],
    keywords='django json logging middleware',
    install_requires=[
        'django>=1.4',
        'six',
        'certifi'
    ]
)
