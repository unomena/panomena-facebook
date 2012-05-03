from setuptools import setup, find_packages

setup(
    name='panomena-facebook',
    description='Panomena Facebook',
    version='0.0.4',
    author='',
    license='Proprietory',
    url='http://www.unomena.com/',
    include_package_data=True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    dependency_links = [
    ],
    install_requires = [
        'Django',
        'panomena-general==0.0.3',
        'panomena-accounts==0.0.5',
    ],
)
