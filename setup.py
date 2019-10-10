from setuptools import setup, find_packages

def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

def readme():
    with open('igclib/README.rst') as f:
        return f.read()

setup(name='igclib',
    version='0.1',
    description='A library for paragliding races',
    long_description=readme(),
    url='https://github.com/teobouvard/igclib',
    author='Téo Bouvard',
    author_email='teobouvard@gmail.com',
    license='MIT',
    packages=find_packages(include=['igclib']),
    install_requires=requirements(),
    scripts=['igclib/bin/race_export', 'igclib/bin/igclib'],
    zip_safe=True)
