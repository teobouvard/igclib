from setuptools import setup, find_packages

VERSION = 0.1

def requirements():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()

def readme():
    with open('docs/source/readme.rst', 'r') as f:
        return f.read()

setup(name='igclib',
    version=VERSION,
    description='A library for paragliding races',
    long_description='',#readme(),
    url='https://github.com/teobouvard/igclib',
    author='Téo Bouvard',
    author_email='teobouvard@gmail.com',
    license='GPL-3',
    packages=find_packages(include=['igclib']),
    install_requires=requirements(),
    scripts=['igclib/bin/igclib'],
    python_requires='>=3.6',
    zip_safe=True)
