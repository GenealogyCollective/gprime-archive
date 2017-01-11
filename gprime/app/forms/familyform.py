#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
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

from gprime.lib.family import Family
from gprime.db import DbTxn

from .forms import Form

class FamilyForm(Form):
    """
    """
    _class = Family
    view = "family"
    tview = "Family"
    table = "Family"

    # Fields for editor:
    edit_fields = [
        "gid",
        "tag_list",
        "private",
        "type"
    ]

    # URL for page view rows:
    link = "/family/%(handle)s"

    # Fields for page view; width sum = 95%:
    select_fields = [
        ("gid", 10),
        ("father_handle", 30),
        ("mother_handle", 30),
        ("type.string", 25),
    ]

    # Default order_by:
    order_by = [("father_surname", "ASC"), ("father_given", "ASC")]

    # Search fields, list is OR:
    search_terms = {
        "father": ["father_surname", "father_given"],
        "mother": ["mother_surname", "mother_given"],
        "id": "gid",
    }

    # Search fields to use if not specified:
    default_search_fields = [
        "father_handle.primary_name.surname_list.0.surname",
        "father_handle.primary_name.first_name",
        "mother_handle.primary_name.surname_list.0.surname",
        "mother_handle.primary_name.first_name",
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

    def set_post_process_functions(self):
        self.post_process_functions = {
            "father_handle": self.get_person_from_handle,
            "mother_handle": self.get_person_from_handle,
            #"tag_list": self.get_tag_from_handle:name
        }

    def delete(self):
        family_handle = self.instance.handle
        with DbTxn(self._("Delete family"), self.database) as transaction:
            for (item, handle) in self.database.find_backlink_handles(family_handle):
                handle_func = self.database.get_table_func(item, "handle_func")
                commit_func = self.database.get_table_func(item, "commit_func")
                obj = handle_func(handle)
                obj.remove_handle_references('Family', [family_handle])
                commit_func(obj, transaction)
            self.database.remove_family(self.instance.handle, transaction)
        self.handler.send_message(self._("Deleted family. <a href='%s'>Undo</a>." % "FIXME"))
        self.handler.redirect(self.handler.app.make_url("/family"))
