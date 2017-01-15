#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Name types.
"""

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import LOCALE as glocale
_ = glocale.translation.gettext

class GenderType(GrampsType):
    _CUSTOM = 3
    _DEFAULT = 2

    _INFO = [
        ( 0, "female", "♀", "she"),
        ( 1, "male", "♂", "he"),
        ( 2, "unknown", "?", "they"),
        ( 3, "custom", "+", "they"),
        ( 4, "homosexual male", "⚣", "he"),
        ( 5, "homosexual female", "⚢", "she"),
        ( 6, "intersex", "☿", "they"),
        ( 7, "transgender", "⚧", "they"),
        ( 8, "transman", "♂", "he"),
        ( 9, "transwoman", "♀", "she"),
        (10, "nonbinary", "☄", "they"),
        (11, "cis male", "♂", "he"),
        (12, "cis female", "♀", "she"),
        (13, "gender fluid", "⚥", "they"),
        ( 2, "other", "⚩", "they"),
    ]

    _DATAMAP = [(base[0], _(base[1]), base[1]) for base in _INFO]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def get_symbol(self):
        return [tup[2] for tup in self._INFO if tup[0] == self.value][0]

    def get_pronoun(self):
        return [tup[3] for tup in self._INFO if tup[0] == self.value][0]

    @classmethod
    def get_male_codes(cls):
        return [tup[0] for tup in cls._INFO if tup[3] == "he"]

    @classmethod
    def get_female_codes(cls):
        return [tup[0] for tup in cls._INFO if tup[3] == "she"]
