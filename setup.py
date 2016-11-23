#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup
import sys


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)


with open('gramps_connect/__init__.py', 'rb') as fid:
    for line in fid:
        line = line.decode('utf-8')
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

setup(name='gramps_connect',
      version=version,
      description='Gramps webapp for genealogy',
      long_description=open('README.md', 'rb').read().decode('utf-8'),
      author='Doug Blank',
      author_email='doug.blank@gmail.org',
      url="https://github.com/gramps-connect/gramps_connect",
      install_requires=['gramps>=5.0', "tornado"],
      packages=['gramps_connect', 
                'gramps_connect.handlers'],
      include_data_files = True,
      include_package_data=True,
      data_files = [("./gramps_connect/templates", 
                     [
                         "gramps_connect/templates/login.html",
                     ])],
      classifiers=[
          "Environment :: Web Environment",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          'Programming Language :: Python :: 3',
          "Topic :: Sociology :: Genealogy",
      ]
)
