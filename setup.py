"""Setup Script.
"""
import os

from setuptools import setup, find_packages

# pylint: disable=invalid-name
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, *('doc', 'README.rst'))) as f:
    README = f.read()
with open(os.path.join(here, 'Changelog')) as f:
    CHANGES = f.read()

requires = [
    'colorlog',
    'Paste',
    'PasteScript',
    'python-dotenv',
    'pyramid',
    'pyramid_assetviews',
    'pyramid_mako',
]

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
    name='puteoli',
    version='0.1',
    description='uPstrem UTility & widgEt hOsting appLIcation',
    long_description=README + '\n\n' + CHANGES,
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
    message_extractors={'puteoli': [
        ('**.py', 'python', None),
        ('static/**', 'ignore', None),
    ]},
    entry_points="""\
    [paste.app_factory]
    main = puteoli:main
    [console_scripts]
    puteoli_pserve = puteoli.scripts.pserve:main
    puteoli_pstart = puteoli.scripts.pstart:main
    """,
)
