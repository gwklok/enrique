import os
import codecs

from setuptools import setup


def read(filename):
    """Read and return `filename` in root dir of project and return string"""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), 'r').read()


install_requires = read("requirements.txt").split()
long_description = read('README.md')


setup(
    name="enrique",
    version="0.1.0",
    url='https://github.com/mesos-magellan/enrique',
    license='MIT License',
    author='Anthony Bilinski',
    description=('Magellan executor'),
    long_description=long_description,
    packages=[],
    install_requires = install_requires,                                                                                                                                                                                                                            
    entry_points={'console_scripts': [
        'enrique = enrique:main'
    ]}
)