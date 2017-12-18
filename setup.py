"""
flask-eureka
-------------
flask extension that provides an interface to eureka via a flask.app
"""


import os.path

from setuptools import setup, find_packages

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))


# Get requirements
requirements = []
with open(os.path.join(LOCAL_DIR, 'requirements.txt'), 'r') as infile:
    for line in infile:
        line = line.strip()
        if line and not line[0] == '#':  # ignore comments
            requirements.append(line)

setup(
    name='flask-eureka',
    packages=find_packages(exclude=['tests*','examples*']),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)