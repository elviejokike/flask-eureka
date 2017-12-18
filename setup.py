"""
flask-eureka
-------------
flask extension that provides an interface to eureka via a flask.app
"""


from setuptools import setup, find_packages

setup(
    name='flask-eureka',
    packages=find_packages(exclude=['tests*','examples*']),
    include_package_data=True,
    install_requires=['Flask'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)