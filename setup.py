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

import sys
import os
import argparse
import glob

from distutils.core import setup
from distutils.command.build import build
from distutils.command.install import install

from distutils.util import convert_path, newer
from distutils import log

# this list MUST be a subset of _LOCALE_NAMES in gen/utils/grampslocale.py
# (that is, if you add a new language here, be sure it's in _LOCALE_NAMES too)
ALL_LINGUAS = ('ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en_GB',
               'eo', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'is', 'it',
               'ja', 'lt', 'nb', 'nl', 'nn', 'pl', 'pt_BR', 'pt_PT',
               'ru', 'sk', 'sl', 'sq', 'sr', 'sv', 'tr', 'uk', 'vi',
               'zh_CN', 'zh_HK', 'zh_TW')
_FILES = ('share/gprime/data/tips.xml', 'share/gprime/data/holidays.xml')

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

with open('gprime/version.py', 'rb') as fid:
    for line in fid:
        line = line.decode('utf-8')
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

# Apparently, if you use one custom command, they all lose their minds:
class Install(install):
    sub_commands = install.sub_commands + [
        ('install_scripts', None),
        ('install_data', None),
        ('install_lib', None),
    ]

class Build(build):
    """Custom build command."""
    sub_commands = install.sub_commands + [
        ('build_scripts', None),
        ('build_py', None),
        ('build_ext', None),
    ]
    def run(self):
        log.info('Build.run()...')
        self.build_trans()
        self.build_intl()
        super().run()

    def build_intl(self):
        '''
        Merge translation files into desktop and mime files
        '''
        for filename in _FILES:
            filename = convert_path(filename)
            self.strip_files(filename + '.in', filename, ['_tip', '_name'])

        i_v = intltool_version()
        if i_v is None or i_v < (0, 25, 0):
            log.info('No intltool or version < 0.25.0, build_intl is aborting')
            return
        data_files = self.distribution.data_files
        base = self.build_base

        merge_files = (('share/gprime/data/gramps.desktop', 'share/applications', '-d'),
                        ('share/gprime/data/gramps.keys', 'share/mime-info', '-k'),
                        ('share/gprime/data/gramps.xml', 'mime/packages', '-x'),
                        ('share/gprime/data/gramps.appdata.xml', 'share/metainfo', '-x'))

        for filename, target, option in merge_files:
            filenamelocal = convert_path(filename)
            newfile = os.path.join(base, filenamelocal)
            newdir = os.path.dirname(newfile)
            if not(os.path.isdir(newdir) or os.path.islink(newdir)):
                os.makedirs(newdir)
            merge(filenamelocal + '.in', newfile, option)
            data_files.append((target, [base + '/' + filename]))

    def build_trans(self):
        '''
        Translate the language files into gramps.mo
        '''
        data_files = self.distribution.data_files
        for lang in ALL_LINGUAS:
            po_file = os.path.join('po', lang + '.po')
            mo_file = os.path.join(self.build_base, 'mo', lang, 'LC_MESSAGES',
                                   'gramps.mo')
            mo_file_unix = (self.build_base + '/mo/' + lang +
                            '/LC_MESSAGES/gramps.mo')
            mo_dir = os.path.dirname(mo_file)
            if not(os.path.isdir(mo_dir) or os.path.islink(mo_dir)):
                os.makedirs(mo_dir)

            if newer(po_file, mo_file):
                cmd = 'msgfmt %s -o %s' % (po_file, mo_file)
                if os.system(cmd) != 0:
                    os.remove(mo_file)
                    msg = 'ERROR: Building language translation files failed.'
                    ask = msg + '\n Continue building y/n [n] '
                    reply = input(ask)
                    if reply in ['n', 'N']:
                        raise SystemExit(msg)
                log.info('Compiling %s >> %s', po_file, mo_file)

            #linux specific piece:
            target = 'share/gprime/locale/' + lang + '/LC_MESSAGES'
            data_files.append((target, [mo_file_unix]))

    def strip_files(self, in_file, out_file, mark):
        '''
        strip the file of the first character (typically an underscore) in each
        keyword (in the "mark" argument list) in the file -- so this method is an
        Alternative to intltool-merge command.
        '''
        if (not os.path.exists(out_file) and os.path.exists(in_file)):
            old = open(in_file, 'r', encoding='utf-8')
            with open(out_file, 'w', encoding='utf-8', errors='strict') as fb:
                for line in old:
                    for marker in mark:
                        line = line.replace(marker, marker[1:])
                    fb.write(line)
            old.close()
            log.info('Compiling %s >> %s', in_file, out_file)

def intltool_version():
    '''
    Return the version of intltool as a tuple.
    '''
    import subprocess
    if sys.platform == 'win32':
        cmd = ["perl", "-e print qx(intltool-update --version) =~ m/(\d+.\d+.\d+)/;"]
        try:
            ver, ret = subprocess.Popen(cmd ,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True).communicate()
            ver = ver.decode("utf-8")
            if ver > "":
                version_str = ver
            else:
                return (0,0,0)
        except:
            return (0,0,0)
    else:
        cmd = 'intltool-update --version 2> /dev/null' # pathological case
        retcode, version_str = subprocess.getstatusoutput(cmd)
        if retcode != 0:
            return None
        cmd = 'intltool-update --version 2> /dev/null | head -1 | cut -d" " -f3'
        retcode, version_str = subprocess.getstatusoutput(cmd)
        if retcode != 0: # unlikely but just barely imaginable, so leave it
            return None
    return tuple([int(num) for num in version_str.split('.')])

def merge(in_file, out_file, option, po_dir='po', cache=True):
    '''
    Run the intltool-merge command.
    '''
    option += ' -u'
    if cache:
        cache_file = os.path.join('po', '.intltool-merge-cache')
        option += ' -c ' + cache_file

    if os.path.exists(in_file):
        if (not os.path.exists(out_file)):
            log.info('Merging %s >> %s', in_file, out_file)
            if sys.platform == 'win32':
                cmd = (('set LC_ALL=C && perl -S intltool-merge %(opt)s %(po_dir)s %(in_file)s '
                    '%(out_file)s') %
                  {'opt' : option,
                   'po_dir' : po_dir,
                   'in_file' : in_file,
                   'out_file' : out_file})
            else:
                cmd = (('LC_ALL=C intltool-merge %(opt)s %(po_dir)s %(in_file)s '
                    '%(out_file)s') %
                  {'opt' : option,
                   'po_dir' : po_dir,
                   'in_file' : in_file,
                   'out_file' : out_file})
            if os.system(cmd) != 0:
                msg = ('ERROR: %s was not merged into the translation files!\n' %
                        out_file)
                raise SystemExit(msg)
            log.info('Compiling %s >> %s', in_file, out_file)
    else:
        raise Exception("merge: unknown input file: %s" % in_file)

def get_data_files(path):
    retval = []
    for folder, subdirs, files in os.walk(path):
        subfolder = []
        for filename in files:
            subfolder.append(os.path.join(folder, filename))
        if subfolder:
            retval.append([folder, subfolder])
    return retval

data_files = get_data_files("share") + [("share/gprime/data/", ["share/gprime/data/authors.xml"])]

# Find all packages:
here = os.path.abspath(os.path.dirname(__file__))
packages = []
for d, _, _ in os.walk(os.path.join(here, "gprime")):
    if os.path.exists(os.path.join(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(os.path.sep, '.'))

setup_args = dict(
    name='gprime',
    cmdclass = {
        'build': Build,
        'install': Install,
    },
    version=version,
    description='gPrime webapp for genealogy',
    long_description=open('README.md', 'rb').read().decode('utf-8'),
    author='Doug Blank',
    author_email='doug.blank@gmail.org',
    url="https://github.com/GenealogyCollective/gprime",
    install_requires=["tornado", "simplejson", "passlib", "meta", "pillow"],
    packages=packages,
    data_files=data_files,
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        'Programming Language :: Python :: 3',
        "Topic :: Sociology :: Genealogy",
    ],
    scripts = glob.glob(os.path.join("scripts", "*"))
)

if 'develop' in sys.argv or any(a.startswith('bdist') for a in sys.argv):
    import setuptools

setuptools_args = {}
setuptools_args["entry_points"] = {
    "console_scripts": [
        "gprime = gprime.app:main",
    ]
}

if 'setuptools' in sys.modules:
    setup_args.update(setuptools_args)
    setup_args.pop('scripts')

if __name__ == '__main__':
    setup(**setup_args)
