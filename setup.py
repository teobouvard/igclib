from setuptools import setup, find_packages
from distutils.core import Extension

VERSION = '0.1.1'

def requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()

def readme():
    with open('readme.md', 'r') as f:
        return f.read()

geolib = Extension('geolib', ['igclib/c_ext/geodesic.c', 'igclib/c_ext/geolib.c'])

setup(name='igclib',
    version=VERSION,
    description='A library for paragliding races',
    long_description=readme(),
    url='https://github.com/teobouvard/igclib',
    author='Téo Bouvard',
    author_email='teobouvard@gmail.com',
    license='GPL-3',
    packages=find_packages(include=['igclib']),
    ext_modules = [geolib],
    install_requires=requirements(),
    scripts=['igclib/bin/igclib'],
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=True)
