#
# gPrime - A web-based genealogy program
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

"""Get the data files for this package."""

def get_data_files(*search_path):
    """
    Walk up until we find search/path
    Example:
    >>> get_data_files("share", "gprime")
    """
    search_path = os.path.join(*search_path)
    path = os.path.abspath(os.path.dirname(__file__))
    starting_points = [path]
    if not path.startswith(sys.prefix):
        starting_points.append(sys.prefix)
    for path in starting_points:
        # walk up, looking for prefix/search/path
        while path != '/':
            location = os.path.join(path, search_path)
            if os.path.exists(location):
                return location
            path, _ = os.path.split(path)
    # didn't find it, give up
    return ''

# Package managers can just override this with the appropriate constant
DATA_FILES_PATH = get_data_files("share", "gprime")

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
        resource_path = DATA_FILES_PATH
        self.data_dir = os.path.join(resource_path, 'data')
        self.image_dir = os.path.join(resource_path, 'images')
        self.locale_dir = os.path.join(resource_path, 'locale')
        # If not installed, use build/mo for translations:
        if not os.path.exists(self.locale_dir):
            self.locale_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__),
                             '..', '..', 'build', 'mo'))
        # Test, give warnings:
        for folder in [self.locale_dir, self.data_dir, self.image_dir]:
            if (not os.path.exists(folder)):
                LOG.error("Unable to find resource on path: %s" % folder)
        self.initialized = True

