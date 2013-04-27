from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='banksucker',
    version='0.0.1',
    packages=['banksucker'],
    install_requires=[
        'lxml',
        'requests',
        ],
    )
