#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    Copyright (C) 2015-2016 Ministry of Health - Jamaica

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from os import path
import ConfigParser

name = 'health_triage_queue'
prefix = 'trytond_'


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

tryton_version = (3, 4, 3, 5)
gnuhealth_version = (2, 8, 2, 9)
jmversion = '>=2.0,<2.1'

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))

for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()


requires = [
    'trytond>=%d.%d,<%d.%d' % tryton_version,
    'trytond_health_encounter>=0.2,<0.3',
    'trytond_health_jamaica' + jmversion
]

setup(
    name=prefix + name,
    version=info.get('version', '0.0.1'),
    description=info.get('description', 'GNU Health Triage and Queue Module'),
    long_description=read('README.rst'),
    author='Marc Murray',
    author_email='murraym@moh.gov.jm',
    url='https://nhin.mohjm.com',
    download_url='https://nhin.mohjm.com/epas',
    package_dir={'trytond.modules.health_triage_queue': '.'},
    packages=[
        'trytond.modules.health_triage_queue',
    ],

    package_data={
        'trytond.modules.health_triage_queue': info.get('xml', [])
            + info.get('translation', [])
            + ['tryton.cfg', 'view/*.xml', 'doc/*.rst', 'locale/*.po',
               'report/*.odt', 'icons/*.svg'],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    health_triage_queue = trytond.modules.health_triage_queue
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
)
