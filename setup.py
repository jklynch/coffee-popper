# -*- encoding: utf-8 -*-
import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='coffee_popper',
    version='0.0',
    license='MIT',
    description='Pop some coffee why not?',
    #long_description='%s\n%s' % (read('README.md'), re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.md'))),
    author='Joshua Lynch',
    author_email='joshua.kevin.lynch@gmail.com',
    url='https://github.com/jklynch/coffee_popper',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Coffee Nuts',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'matplotlib', 'pyzmq'
    ],
    extras_require={
        'test': ['pytest', ],
    },
    entry_points={
        'console_scripts': [
            'roast = coffee_popper.__main__:main',
        ]
    },
)
