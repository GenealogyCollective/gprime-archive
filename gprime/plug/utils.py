#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2009 B. Malengier
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

"""
General utility functions useful for the generic plugin system
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import sys
import os
import datetime
from io import StringIO, BytesIO

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".gen.plug")

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from ._pluginreg import make_environment
from gprime.version import VERSION_TUPLE
from . import BasePluginManager
from ..utils.configmanager import safe_eval
from ..config import config
from ..const import LOCALE as glocale
_ = glocale.translation.sgettext
from ..constfunc import mac

#-------------------------------------------------------------------------
#
# Local utility functions for gen.plug
#
#-------------------------------------------------------------------------
def version_str_to_tup(sversion, positions):
    """
    Given a string version and positions count, returns a tuple of
    integers.

    >>> version_str_to_tup("1.02.9", 2)
    (1, 2)
    """
    try:
        tup = tuple(map(int, sversion.split(".")))
        tup += (0,) * (positions - len(tup))
    except:
        tup = (0,) * positions
    return tup[:positions]

class newplugin:
    """
    Fake newplugin.
    """
    def __init__(self):
        globals()["register_results"].append({})
    def __setattr__(self, attr, value):
        globals()["register_results"][-1][attr] = value

def register(ptype, **kwargs):
    """
    Fake registration. Side-effect sets register_results to kwargs.
    """
    retval = {"ptype": ptype}
    retval.update(kwargs)
    # Get the results back to calling function
    if "register_results" in globals():
        globals()["register_results"].append(retval)
    else:
        globals()["register_results"] = [retval]

class Zipfile:
    """
    Class to duplicate the methods of tarfile.TarFile, for Python 2.5.
    """
    def __init__(self, buffer):
        import zipfile
        self.buffer = buffer
        self.zip_obj = zipfile.ZipFile(buffer)

    def extractall(self, path, members=None):
        """
        Extract all of the files in the zip into path.
        """
        names = self.zip_obj.namelist()
        for name in self.get_paths(names):
            fullname = os.path.join(path, name)
            if not os.path.exists(fullname):
                os.mkdir(fullname)
        for name in self.get_files(names):
            fullname = os.path.join(path, name)
            outfile = file(fullname, 'wb')
            outfile.write(self.zip_obj.read(name))
            outfile.close()

    def extractfile(self, name):
        """
        Extract a name from the zip file.

        >>> Zipfile(buffer).extractfile("Dir/dile.py").read()
        <Contents>
        """
        class ExtractFile:
            def __init__(self, zip_obj, name):
                self.zip_obj = zip_obj
                self.name = name
            def read(self):
                data = self.zip_obj.read(self.name)
                del self.zip_obj
                return data
        return ExtractFile(self.zip_obj, name)

    def close(self):
        """
        Close the zip object.
        """
        self.zip_obj.close()

    def getnames(self):
        """
        Get the files and directories of the zipfile.
        """
        return self.zip_obj.namelist()

    def get_paths(self, items):
        """
        Get the directories from the items.
        """
        return (name for name in items if self.is_path(name) and not self.is_file(name))

    def get_files(self, items):
        """
        Get the files from the items.
        """
        return (name for name in items if self.is_file(name))

    def is_path(self, name):
        """
        Is the name a path?
        """
        return os.path.split(name)[0]

    def is_file(self, name):
        """
        Is the name a directory?
        """
        return os.path.split(name)[1]

def urlopen_maybe_no_check_cert(URL):
    """
    Similar to urllib.request.urlopen, but disables certificate
    verification on Mac.
    """
    context = None
    from urllib.request import urlopen
    if mac():
        from ssl import create_default_context, CERT_NONE
        context = create_default_context()
        context.check_hostname = False
        context.verify_mode = CERT_NONE
    timeout = 10 # seconds
    fp = None
    try:
        fp = urlopen(URL, timeout=timeout, context=context)
    except TypeError:
        fp = urlopen(URL, timeout=timeout)
    return fp

def available_updates():
    whattypes = config.get('behavior.check-for-update-types')

    LOG.debug("Checking for updated addons...")
    langs = glocale.get_language_list()
    langs.append("en")
    # now we have a list of languages to try:
    fp = None
    for lang in langs:
        URL = ("%s/listings/addons-%s.txt" %
               (config.get("behavior.addons-url"), lang))
        LOG.debug("   trying: %s" % URL)
        try:
            fp = urlopen_maybe_no_check_cert(URL)
        except:
            try:
                URL = ("%s/listings/addons-%s.txt" %
                       (config.get("behavior.addons-url"), lang[:2]))
                fp = urlopen_maybe_no_check_cert(URL)
            except Exception as err: # some error
                LOG.warning("Failed to open addon metadata for {lang} {url}: {err}".
                        format(lang=lang, url=URL, err=err))
                fp = None
        if fp and fp.getcode() == 200: # ok
            break

    pmgr = BasePluginManager.get_instance()
    addon_update_list = []
    if fp and fp.getcode() == 200:
        lines = list(fp.readlines())
        count = 0
        for line in lines:
            line = line.decode('utf-8')
            try:
                plugin_dict = safe_eval(line)
                if type(plugin_dict) != type({}):
                    raise TypeError("Line with addon metadata is not "
                                    "a dictionary")
            except:
                LOG.warning("Skipped a line in the addon listing: " +
                         str(line))
                continue
            id = plugin_dict["i"]
            plugin = pmgr.get_plugin(id)
            if plugin:
                LOG.debug("Comparing %s > %s" %
                          (version_str_to_tup(plugin_dict["v"], 3),
                           version_str_to_tup(plugin.version, 3)))
                if (version_str_to_tup(plugin_dict["v"], 3) >
                    version_str_to_tup(plugin.version, 3)):
                    LOG.debug("   Downloading '%s'..." % plugin_dict["z"])
                    if "update" in whattypes:
                        if (not config.get('behavior.do-not-show-previously-seen-updates') or
                             plugin_dict["i"] not in config.get('behavior.previously-seen-updates')):
                            addon_update_list.append((_("Updated"),
                                                      "%s/download/%s" %
                                                      (config.get("behavior.addons-url"),
                                                       plugin_dict["z"]),
                                                      plugin_dict))
                else:
                    LOG.debug("   '%s' is ok" % plugin_dict["n"])
            else:
                LOG.debug("   '%s' is not installed" % plugin_dict["n"])
                if "new" in whattypes:
                    if (not config.get('behavior.do-not-show-previously-seen-updates') or
                         plugin_dict["i"] not in config.get('behavior.previously-seen-updates')):
                        addon_update_list.append((_("updates|New"),
                                                  "%s/download/%s" %
                                                  (config.get("behavior.addons-url"),
                                                   plugin_dict["z"]),
                                                  plugin_dict))
        config.set("behavior.last-check-for-updates",
                   datetime.date.today().strftime("%Y/%m/%d"))
        count += 1
        if fp:
            fp.close()
    else:
        LOG.debug("Checking Addons Failed")
    LOG.debug("Done checking!")

    return addon_update_list

#-------------------------------------------------------------------------
#
# OpenFileOrStdout class
#
#-------------------------------------------------------------------------
class OpenFileOrStdout:
    """Context manager to open a file or stdout for writing."""
    def __init__(self, filename, encoding=None, errors=None, newline=None):
        self.filename = filename
        self.filehandle = None
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

    def __enter__(self):
        if self.filename == '-':
            self.filehandle = sys.stdout
        else:
            self.filehandle = open(self.filename, 'w', encoding=self.encoding,
                                   errors=self.errors, newline=self.newline)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filehandle and self.filename != '-':
            self.filehandle.close()
        return False

#-------------------------------------------------------------------------
#
# OpenFileOrStdin class
#
#-------------------------------------------------------------------------
class OpenFileOrStdin:
    """Context manager to open a file or stdin for reading."""
    def __init__(self, filename, add_mode='', encoding=None):
        self.filename = filename
        self.mode = 'r%s' % add_mode
        self.filehandle = None
        self.encoding = encoding

    def __enter__(self):
        if self.filename == '-':
            self.filehandle = sys.stdin
        elif self.encoding:
            self.filehandle = open(self.filename, self.mode, encoding=self.encoding)
        else:
            self.filehandle = open(self.filename, self.mode)
        return self.filehandle

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename != '-':
            self.filehandle.close()
        return False
