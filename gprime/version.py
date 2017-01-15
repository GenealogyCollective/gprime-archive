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

## "-alpha", "-beta", "-beta1" is optional:
__version__ = "1.0.9-alpha2"
VERSION        = __version__
# three numbers, semantic versioning:
VERSION_TUPLE = tuple([int(number) for number in __version__.split("-")[0].split(".")])
# two string numbers, semantic versioning:
major_version = "%s.%s" % (VERSION_TUPLE[0], VERSION_TUPLE[1])
