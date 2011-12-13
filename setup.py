# -*- coding: utf8 -*-

from setuptools import setup
from setuptools import find_packages


setup(
    name='duende',
    version='0.0.12',
    author='Jerónimo José Albi',
    author_email='jeronimo.albi@gmail.com',
    description='Duende web framework',
    long_description='',
    url='https://github.com/jeronimoalbi/duende',
    keywords='web wsgi framework sqlalchemy formencode jinja2 templates',
    license='BSD',
    scripts=[
        'scripts/duende-export.py',
    ],
    install_requires=[
        'simplejson',
        'Paste>=1.7',
        'PasteDeploy>=1.5',
        'PasteScript>=1.7',
        'WebOb',
        'Beaker',
        'Jinja2',
        'Babel',
        'SQLAlchemy>=0.7',
        'FormEncode',
    ],
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Paste",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            "duende_shell = duende.lib.command:shell",
        ],
        'paste.paster_create_template': [
            "duende = duende.lib.pastetemplate:DuendeProjectTemplate",
        ]
    },
)
