#!/usr/bin/env python

from setuptools import setup, find_packages
import sys
import uuid
try:
    from pip.req import parse_requirements
except Exception:
    sys.stderr.write("can't import, "
                     "probably because your python is too old!\n"
                     "please use python 3.0 or later\n")

# sys.version_info(major=3, minor=4, micro=3, releaselevel='final', serial=0)
if sys.version_info < (3, 0):
    sys.stderr.write("You need python 3.0 or later to run this script\n")
    exit(1)

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
requirements = [str(ir.req) for ir in install_reqs]

tests_require = [
    'Flask-RESTful[paging]',
    'mock==0.8',
    'blinker==1.3',
    'urlparse2==1.1.1',
    'coverage==4.0a5'
]


setup(
    name='mc',
    version='0.0.1',
    url='https://github.com/arvin-chou/mc',
    author='arvin chou',
    author_email='arvin.chou.tw@gmail.com',
    description='',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite='nose.collector',
    install_requires=requirements,
    tests_require=tests_require,
    # dependency_links=[
    #    'https://github.com/my_account/private_repo_1/master/tarball/',
    #    'https://github.com/my_account/private_repo_2/master/tarball/',
    # ],
    # Install these with "pip install -e '.[paging]'" or '.[docs]'
    extras_require={
        'paging': 'pycrypto==2.6',
        'docs': 'sphinx',
    },
    scripts=['scripts/install.sh']
)
