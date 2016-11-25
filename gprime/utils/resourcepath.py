#
# Gprime - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
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
import logging
LOG = logging.getLogger("ResourcePath")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
LOG.addHandler(_hdlr)

from ..constfunc import get_env_var

class ResourcePath:
    """
    ResourcePath is a singleton, meaning that only one of them is ever
    created.  At startup it finds the paths to Gramps's resource files and
    caches them for future use.

    It should be called only by const.py; other code should retrieve the
    paths from there.
    """
    instance = None
    def __new__(cls):
        if not cls.instance:
            cls.instance = super(ResourcePath, cls).__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self):
        if self.initialized:
            return
        # Look for "resource-path" file right here:
        resource_file = os.path.abspath(
            os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'resource-path'))
        # If exists, we are installed:
        installed = os.path.exists(resource_file)
        resource_path = None
        if installed:
            try:
                with open(resource_file, encoding='utf-8',
                                errors='strict') as fp:
                    resource_path = fp.readline()
            except UnicodeError as err:
                LOG.exception("Encoding error while parsing resource path", err)
                sys.exit(1)
            except IOError as err:
                LOG.exception("Failed to open resource file", err)
                sys.exit(1)
        else: # Local:
            resource_path = os.path.abspath(
                os.path.join(os.path.abspath(os.path.dirname(
                __file__)), "..", ".."))
        if installed:
            # For example, "share/gprime":
            self.locale_dir = os.path.join(resource_path, 'locale')
            self.data_dir = os.path.join(resource_path, 'data')
            self.image_dir = os.path.join(resource_path, 'data', 'images')
        else:
            # gprime local directory:
            self.locale_dir = os.path.join(resource_path, 'build', 'mo')
            self.data_dir = os.path.join(resource_path, 'data')
            self.image_dir = os.path.join(resource_path, 'images')

        for folder in [self.locale_dir, self.data_dir, self.image_dir]:
            if (not os.path.exists(folder)):
                LOG.error("Unable to find resource on path: %s" % folder)
                #sys.exit(1)
            
        self.initialized = True


