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
    _INFO = {
        "Female":            ( 0, "♀", "she"),
        "Male":              ( 1, "♂", "he"),
        "Unknown":           ( 2, "?", "they"),
        "Custom":            ( 3, "+", "they"),
        "Homosexual Male":   ( 4, "⚣", "he"),
        "Homosexual Female": ( 5, "⚢", "she"),
        "Intersex":          ( 6, "☿", "they"),
        "Transgender":       ( 7, "⚧", "they"),
        "Transman":          ( 8, "♂", "he"),
        "Transwoman":        ( 9, "♀", "she"),
        "Nonbinary":         (10, "☄", "they"),
        "Cis Man":           (11, "♂", "he"),
        "Cis Female":        (12, "♀", "she"),
        "Gender fluid":      (13, "⚥", "they"),
        "Other":             (14, "⚩", "they"),
    }

    _CUSTOM = _INFO["Custom"][0]
    _DEFAULT = _INFO["Unknown"][0]

    _DATAMAP = [(_INFO[key][0], _(key), key) for key in _INFO.keys()]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def get_value(self, key):
        return self._INFO[key][0]

    def get_symbol(self, key):
        return self._INFO[key][1]

    def get_pronoun(self, key):
        return self._INFO[key][3]
