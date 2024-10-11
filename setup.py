from setuptools import setup, find_packages

setup(
    name='csvtools',
    version='1.0.0',
    description='A CSV display and debugging tool.',
    author='Rawsab Said',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'csvt=csvtools.csvtools:main',
        ],
    },
    package_data={
        'csvtools': ['csvtoolsConfig.json'],
    },
)
