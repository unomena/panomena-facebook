from setuptools import setup, find_packages

setup(
    name='panomena-facebook',
    description='Panomena Facebook',
    version='0.0.2',
    author='',
    license='Proprietory',
    url='http://www.unomena.com/',
    include_package_data=True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    dependency_links = [
        'http://github.com/unomena/panomena-general/tarball/master#egg=panomena-general',
        'http://github.com/unomena/panomena-accounts/tarball/0.0.2#egg=panomena_accounts-0.0.2',
    ],
    install_requires = [
        'Django==1.2.5',
        'panomena-general==0.0.1',
        'panomena-accounts==0.0.2',
    ],
)
