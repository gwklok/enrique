import os
import codecs

from setuptools import setup, find_packages


def read(filename):
    """Read and return `filename` in root dir of project and return string"""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), 'r').read()


long_description = read('README.md')


setup(
    name="enrique",
    version="0.1.0",
    url='https://github.com/mesos-magellan/enrique',
    license='MIT License',
    author='Anthony Bilinski',
    description=('Magellan executor'),
    long_description=long_description,
    packages=find_packages(),
    # FIXME installing this way breaks the pyrallelsa package
    # use reqs in the meantime
    # install_requires = ['pyrallelsa'],
    # dependency_links=[
    #     'git+git://github.com/mesos-magellan/pyrallelsa#egg=pyrallelsa'
    # ],
    entry_points={'console_scripts': [
        'enrique = enrique:main'
    ]}
)
