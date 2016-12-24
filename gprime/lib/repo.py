#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
Repository object for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .notebase import NoteBase
from .addressbase import AddressBase
from .urlbase import UrlBase
from .tagbase import TagBase
from .repotype import RepositoryType
from .handle import Handle
from .citationbase import IndirectCitationBase

#-------------------------------------------------------------------------
#
# Repository class
#
#-------------------------------------------------------------------------
class Repository(NoteBase, AddressBase, UrlBase, IndirectCitationBase,
                 PrimaryObject):
    """A location where collections of Sources are found."""

    def __init__(self, db=None):
        """
        Create a new Repository instance.
        """
        PrimaryObject.__init__(self)
        NoteBase.__init__(self)
        AddressBase.__init__(self)
        UrlBase.__init__(self)
        self.type = RepositoryType()
        self.name = ""
        self.db = db

    @classmethod
    def get_labels(cls, _):
        return {
            "handle": _("Handle"),
            "gid": _("ID"),
            "type": _("Type"),
            "name": _("Name"),
            "note_list": _("Notes"),
            "address_list": _("Addresses"),
            "urls": _("URLs"),
            "change": _("Last changed"),
            "tag_list": _("Tags"),
            "private": _("Private")
        }

    @classmethod
    def get_table(cls):
        """
        Return abstract Table for database defintions.
        """
        from .struct import Table, Column
        return Table(cls,
            [Column("handle", "VARCHAR(50)",
              primary=True, null=False, index=True),
             Column("gid", "TEXT", index=True),
             Column("json_data", "TEXT")])

    @classmethod
    def get_schema(cls):
        """
        Return the schema as a dictionary for this class.
        """
        from .address import Address
        from .url import Url
        return {
            "handle": Handle("Repository", "REPOSITORY-HANDLE"),
            "gid": str,
            "type": RepositoryType,
            "name": str,
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "address_list": [Address],
            "urls": [Url],
            "change": int,
            "tag_list": [Handle("Tag", "TAG-HANDLE")],
            "private": bool
        }

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
        return {"_class": "Repository",
                "handle": Handle("Repository", self.handle),
                "gid": self.gid,
                "type": self.type.to_struct(),
                "name": str(self.name),
                "note_list": NoteBase.to_struct(self),
                "address_list": AddressBase.to_struct(self),
                "urls": UrlBase.to_struct(self),
                "change": self.change,
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    @classmethod
    def from_struct(cls, struct, self=None):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Repository()
        if not self:
            self = default
        data = (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("gid", default.gid),
                RepositoryType.from_struct(struct.get("type", {})),
                struct.get("name", default.name),
                struct.get("change", default.change),
                struct.get("private", default.private))
        (self.handle, self.gid, self.type, self.name,
         self.change, self.private) = data
        NoteBase.set_from_struct(self, struct)
        AddressBase.set_from_struct(self, struct)
        UrlBase.set_from_struct(self, struct)
        TagBase.set_from_struct(self, struct)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.name, str(self.type)]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.address_list + self.urls

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may
                  refer citations.
        :rtype: list
        """
        return self.address_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return self.address_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return (self.get_referenced_note_handles() +
                self.get_referenced_tag_handles())

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this repository.

        :param acquisition: The repository to merge with the present repository.
        :type acquisition: Repository
        """
        self._merge_privacy(acquisition)
        self._merge_address_list(acquisition)
        self._merge_url_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_type(self, the_type):
        """
        :param the_type: descriptive type of the Repository
        :type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        :returns: the descriptive type of the Repository
        :rtype: str
        """
        return self.type

    def set_name(self, name):
        """
        :param name: descriptive name of the Repository
        :type name: str
        """
        self.name = name

    def get_name(self):
        """
        :returns: the descriptive name of the Repository
        :rtype: str
        """
        return self.name
