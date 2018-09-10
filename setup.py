"""
flask-eureka
-------------
flask extension that provides an interface to eureka via a flask.app
"""

from setuptools import setup, find_packages

setup(
    name='flask-eureka',
    version='0.1.0',
    author='Kike',
    url='https://github.com/elviejokike/flask-eureka',
    keywords=[
        'microservice',
        'netflix',
        'flask',
        'eureka'
    ],
    packages=find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    install_requires=['Flask', 'dnspython', 'urllib3'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
