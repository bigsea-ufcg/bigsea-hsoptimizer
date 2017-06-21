from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='Horizontal Scaling Optimizer',

    version='0.1.0',

    description='Flask service that calculates uses prediction to calculate free resources or host machines',

    url='',

    author='Telles Nobrega',
    author_email='tellesnobrega@gmail.com',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: Apache 2.0',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',

    ],
    keywords='webservice horizontal_scaling application management',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['flask'],

    entry_points={
        'console_scripts': [
            'horizontal_scaling_optimizer=horizontal_scaling_optimizer.cli.main:main',
        ],
    },
)


