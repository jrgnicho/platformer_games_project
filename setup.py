# -*- coding: utf-8 -*-
# Inspired by example in: 
# - https://docs.python-guide.org/writing/structure/
# - https://github.com/navdeep-G/samplemod
# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

#with open('LICENSE') as f:
#    license = f.read()

setup(
    name='platformer_games_project',
    version='0.1.0',
    description='Platformer SDK',
    long_description=readme,
    author='Jorge Nicho',
    author_email='jrgnichodevel@gmail.com',
    #url='https://github.com/kennethreitz/samplemod',
    #license=license,
    packages=find_packages(exclude=('deprecated', 'docs'))
)
