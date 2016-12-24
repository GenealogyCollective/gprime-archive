#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
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
Repository Reference class for Gramps
"""

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .privacybase import PrivacyBase
from .notebase import NoteBase
from .refbase import RefBase
from .srcmediatype import SourceMediaType
from .const import IDENTICAL, EQUAL, DIFFERENT
from .handle import Handle

#-------------------------------------------------------------------------
#
# Repository Reference for Sources
#
#-------------------------------------------------------------------------
class RepoRef(SecondaryObject, PrivacyBase, NoteBase, RefBase):
    """
    Repository reference class.
    """

    def __init__(self, source=None):
        PrivacyBase.__init__(self, source)
        NoteBase.__init__(self, source)
        RefBase.__init__(self, source)
        if source:
            self.call_number = source.call_number
            self.media_type = SourceMediaType(source.media_type)
        else:
            self.call_number = ""
            self.media_type = SourceMediaType()

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {
            "_class": "RepositoryRef",
            "note_list": NoteBase.to_struct(self),
            "ref": Handle("Repository", self.ref),
            "call_number": self.call_number,
            "media_type": self.media_type.to_struct(),
            "private": PrivacyBase.to_struct(self),
            }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        self = default = RepoRef()
        data = (
            struct.get("call_number", default.call_number),
            SourceMediaType.from_struct(struct.get("media_type", {})),
            )
        (self.call_number, self.media_type) = data
        PrivacyBase.set_from_struct(self, struct)
        NoteBase.set_from_struct(self, struct)
        RefBase.set_from_struct(self, struct)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.call_number, str(self.media_type)]

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        ret = self.get_referenced_note_handles()
        if self.ref:
            ret += [('Repository', self.ref)]
        return ret

    def is_equivalent(self, other):
        """
        Return if this repository reference is equivalent, that is agrees in
        reference, call number and medium, to other.

        :param other: The repository reference to compare this one to.
        :type other: RepoRef
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.ref != other.ref or \
            self.get_text_data_list() != other.get_text_data_list():
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this repository reference.

        :param acquisition: The repository reference to merge with the present
                            repository reference.
        :type acquisition: RepoRef
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)

    def set_call_number(self, number):
        self.call_number = number

    def get_call_number(self):
        return self.call_number

    def get_media_type(self):
        return self.media_type

    def set_media_type(self, media_type):
        self.media_type.set(media_type)
