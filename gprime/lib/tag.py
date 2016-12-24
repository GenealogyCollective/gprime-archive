#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2010      Nick Hall
# Copyright (C) 2013      Doug Blank <doug.blank@gmail.com>
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
Tag object for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .tableobj import TableObject
from .handle import Handle

#-------------------------------------------------------------------------
#
# Tag class
#
#-------------------------------------------------------------------------
class Tag(TableObject):
    """
    The Tag record is used to store information about a tag that can be
    attached to a primary object.
    """

    def __init__(self, db=None):
        """
        Create a new Tag instance, copying from the source if present.

        :param source: A tag used to initialize the new tag
        :type source: Tag
        """

        TableObject.__init__(self)
        self.db = db
        self.__name = ""
        self.__color = "#000000000000" # Black
        self.__priority = 0

    @classmethod
    def get_schema(cls):
        """
        Return the schema for Tag
        """
        return {
            "handle": Handle("Tag", "TAG-HANDLE"),
            "name": str,
            "color": str,
            "priority": int,
            "change": int,
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
             Column("order_by", "TEXT", index=True),
             Column("json_data", "TEXT")])

    @classmethod
    def get_labels(cls, _):
        """
        Return the label for fields
        """
        return {
            "handle": _("Handle"),
            "name": _("Name"),
            "color": _("Color"),
            "priority": _("Priority"),
            "change": _("Last changed"),
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.__name]

    def is_empty(self):
        """
        Return True if the Tag is an empty object (no values set).

        :returns: True if the Tag is empty
        :rtype: bool
        """
        return self.__name != ""

    def are_equal(self, other):
        """
        Return True if the passed Tag is equivalent to the current Tag.

        :param other: Tag to compare against
        :type other: Tag
        :returns: True if the Tags are equal
        :rtype: bool
        """
        if other is None:
            other = Tag()

        if (self.__name != other.name or
                self.__color != other.color or
                self.__priority != other.priority):
            return False
        return True

    def set_name(self, name):
        """
        Set the name of the Tag to the passed string.

        :param name: Name to assign to the Tag
        :type name: str
        """
        self.__name = name

    def get_name(self):
        """
        Return the name of the Tag.

        :returns: Name of the Tag
        :rtype: str
        """
        return self.__name
    name = property(get_name, set_name, None,
                    'Returns or sets name of the tag')

    def set_color(self, color):
        """
        Set the color of the Tag to the passed string.

        The string is of the format #rrrrggggbbbb.

        :param color: Color to assign to the Tag
        :type color: str
        """
        self.__color = color

    def get_color(self):
        """
        Return the color of the Tag.

        :returns: Returns the color of the Tag
        :rtype: str
        """
        return self.__color
    color = property(get_color, set_color, None,
                     'Returns or sets color of the tag')

    def set_priority(self, priority):
        """
        Set the priority of the Tag to the passed integer.

        The lower the value the higher the priority.

        :param priority: Priority to assign to the Tag
        :type priority: int
        """
        self.__priority = priority

    def get_priority(self):
        """
        Return the priority of the Tag.

        :returns: Returns the priority of the Tag
        :rtype: int
        """
        return self.__priority

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
        return {"_class": "Tag",
                "handle": Handle("Tag", self.handle),
                "name": self.__name,
                "color": self.__color,
                "priority": self.__priority,
                "change": self.change}

    @classmethod
    def from_struct(cls, struct, self=None):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Tag()
        if not self:
            self = default
        data = (Handle.from_struct(struct.get("handle", default.handle)),
                struct.get("name", default.name),
                struct.get("color", default.color),
                struct.get("priority", default.priority),
                struct.get("change", default.change))
        (self.handle,
         self.__name,
         self.__color,
         self.__priority,
         self.change) = data
        return self

    priority = property(get_priority, set_priority, None,
                        'Returns or sets priority of the tag')
