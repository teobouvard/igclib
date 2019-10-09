from setuptools import setup, find_packages

setup(name='igclib',
    version='0.1',
    description='A library for paragliding races',
    url='https://github.com/teobouvard/igclib',
    author='Téo Bouvard',
    author_email='teobouvard@gmail.com',
    license='MIT',
    packages=find_packages(include=['igclib']),
    zip_safe=True)
