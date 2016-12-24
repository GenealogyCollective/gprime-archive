#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2010       Nick Hall
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
Media object for Gramps.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
from urllib.parse import urlparse
import logging

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .citationbase import CitationBase
from .notebase import NoteBase
from .datebase import DateBase
from .attrbase import AttributeBase
from .tagbase import TagBase
from .handle import Handle

LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# Media class
#
#-------------------------------------------------------------------------
class Media(CitationBase, NoteBase, DateBase, AttributeBase,
                  PrimaryObject):
    """
    Container for information about an image file, including location,
    description and privacy.
    """

    def __init__(self, db=None):
        """
        Initialize a Media.

        If source is not None, then object is initialized from values of the
        source object.

        :param source: Object used to initialize the new object
        :type source: Media
        """
        PrimaryObject.__init__(self)
        CitationBase.__init__(self)
        NoteBase.__init__(self)
        DateBase.__init__(self)
        AttributeBase.__init__(self)
        self.db = db
        self.path = ""
        self.mime = ""
        self.desc = ""
        self.checksum = ""
        self.thumb = None

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
        return {"_class": "Media",
                "handle": Handle("Media", self.handle),
                "gid": self.gid,
                "path": self.path,
                "mime": self.mime,
                "desc": self.desc,
                "checksum": self.checksum,
                "attribute_list": AttributeBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "change": self.change,
                "date": DateBase.to_struct(self),
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    @classmethod
    def get_table(cls):
        """
        Return abstract Table for database defintions.
        """
        from .struct import Table, Column
        return Table(cls,
            [Column("handle", "VARCHAR(50)",
              primary=True, null=False, index=True),
             Column("order_by", "TEXT", index=True),
             Column("gid", "TEXT", index=True),
             Column("json_data", "TEXT")])

    @classmethod
    def get_schema(cls):
        """
        Returns the schema for EventRef.

        :returns: Returns a dict containing the fields to types.
        :rtype: dict
        """
        from .attribute import Attribute
        from .date import Date
        return {
            "handle": Handle("Media", "MEDIA-HANDLE"),
            "gid": str,
            "path": str,
            "mime": str,
            "desc": str,
            "checksum": str,
            "attribute_list": [Attribute],
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "change": int,
            "date": Date,
            "tag_list": [Handle("Tag", "TAG-HANDLE")],
            "private": bool,
        }

    @classmethod
    def get_labels(cls, _):
        """
        Given a translation function, returns the labels for
        each field of this object.

        :returns: Returns a dict containing the fields to labels.
        :rtype: dict
        """
        return {
            "_class": _("Media"),
            "handle": _("Media"),
            "gid": _("ID"),
            "path": _("Path"),
            "mime": _("MIME"),
            "desc": _("Description"),
            "checksum": _("Checksum"),
            "attribute_list": _("Attributes"),
            "citation_list": _("Citations"),
            "note_list": _("Notes"),
            "change": _("Last changed"),
            "date": _("Date"),
            "tag_list": _("Tags"),
            "private": _("Private"),
        }

    @classmethod
    def from_struct(cls, struct, self=None):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        from .date import Date
        default = Media()
        if not self:
            self = default
        data = (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("gid", default.gid),
                struct.get("path", default.path),
                struct.get("mime", default.mime),
                struct.get("desc", default.desc),
                struct.get("checksum", default.checksum),
                struct.get("change", default.change),
                Date.from_struct(struct.get("date", {})),
                struct.get("private", default.private))
        (self.handle, self.gid, self.path, self.mime, self.desc,
         self.checksum, self.change,
         self.date, self.private) = data
        AttributeBase.set_from_struct(self, struct)
        CitationBase.set_from_struct(self, struct)
        NoteBase.set_from_struct(self, struct)
        DateBase.set_from_struct(self, struct)
        TagBase.set_from_struct(self, struct)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.path, self.mime, self.desc, self.gid]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer to citations.

        :returns: Returns the list of child secondary child objects that may
                  refer to citations.
        :rtype: list
        """
        return self.attribute_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return self.attribute_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles() + \
               self.get_referenced_tag_handles()  + \
               self.get_referenced_citation_handles()

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list()

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this media object.

        Lost: handle, id, file, date of acquisition.

        :param acquisition: The media object to merge with the present object.
        :type acquisition: Media
        """
        self._merge_privacy(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)
        self._merge_tag_list(acquisition)

    def set_mime_type(self, mime_type):
        """
        Set the MIME type associated with the Media.

        :param mime_type: MIME type to be assigned to the object
        :type mime_type: str
        """
        self.mime = mime_type

    def get_mime_type(self):
        """
        Return the MIME type associated with the Media.

        :returns: Returns the associated MIME type
        :rtype: str
        """
        return self.mime

    def set_path(self, path):
        """Set the file path to the passed path."""
        res = urlparse(path)
        if res.scheme == '' or res.scheme == 'file':
            self.path = os.path.normpath(path)
        else:
            # The principal case this path caters for is where the scheme is
            # 'http' or 'https'. It would be possible to do some more extensive
            # checking or processing, but for now we just store the reference
            self.path = path

    def get_path(self):
        """Return the file path."""
        return self.path

    def set_description(self, text):
        """Set the description of the image."""
        self.desc = text

    def get_description(self):
        """Return the description of the image."""
        return self.desc

    def set_checksum(self, text):
        """Set the checksum of the image."""
        self.checksum = text

    def get_checksum(self):
        """Return the checksum of the image."""
        return self.checksum
