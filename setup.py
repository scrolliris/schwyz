import os
import sys

from setuptools import setup, find_packages

# pylint: disable=invalid-name
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, *('doc', 'DESCRIPTION.rst'))) as f:
    DESCRIPTION = f.read()
with open(os.path.join(here, 'CHANGELOG')) as f:
    CHANGELOG = f.read()

requires = [
    'boto3',
    'colorlog',
    'google-cloud-datastore',
    'Paste',
    'PasteScript',
    'python-dotenv',
    'pyramid',
    'pyramid_assetviews',
    'pyramid_mako',
    'pyramid_services',
    'pytz',
]

if sys.version_info[0] < 3:  # python 2.7
    requires.extend([
        'ipaddress',
        'typing',
    ])

development_requires = [
    'flake8',
    'pylint',
    'waitress',
]

testing_requires = [
    'pytest',
    'pytest-cov',
    'WebTest',
]

production_requires = [
    'CherryPy',
    'raven',
]

setup(
    name='schwyz',
    version='0.1',
    description='schwyz',
    long_description=DESCRIPTION + '\n\n' + CHANGELOG,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'development': development_requires,
        'testing': testing_requires,
        'production': production_requires,
    },
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = schwyz:main
    [console_scripts]
    schwyz_pserve = schwyz.scripts.pserve:main
    schwyz_pstart = schwyz.scripts.pstart:main
    schwyz_manage = schwyz.scripts.manage:main
    """,
)
