from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='igclib',
    version='0.1',
    description='A library for paragliding races',
    url='https://github.com/teobouvard/igclib',
    author='Téo Bouvard',
    author_email='teobouvard@gmail.com',
    license='MIT',
    packages=find_packages(include=['igclib']),
    install_requires=requirements,
    zip_safe=True)
