#! /usr/bin/env python
#
# Copyright (C) 2015 zulily, llc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pudl setup"""

from setuptools import setup, find_packages

execfile('pudl/version.py')

setup(name='pudl',
      version=__version__,
      description="""pudl is an Active Directory client library and CLI""",
      author='zulily, llc',
      author_email='opensource@zulily.com',
      packages=find_packages(),
      url='https://github.com/zulily/pudl',
      license='Apache License, Version 2.0',
      entry_points={
          'console_scripts': [
              'pudl = pudl.scripts.cli:main'
          ]
      },
      install_requires=[
          'python-ldap',
          'pyyaml'
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Systems Administration',
          'Topic :: System :: Systems Administration :: Authentication/Directory',
          'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
      ],
)
