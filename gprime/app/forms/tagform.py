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

# Gramps imports:
from gprime.lib.tag import Tag
from gprime.db import DbTxn

# Gramps Connect imports:
from .forms import Form

class TagForm(Form):
    """
    A form for listing, viewing, and editing a Person object.
    """
    _class = Tag
    view = "tag"
    tview = "Tag"
    table = "Tag"

    # Fields for editor:
    edit_fields = [
        "name",
        "color",
        "priority",
    ]

    # URL for page view rows:
    link = "/tag/%(handle)s"

    # Search fields to use if not specified:
    default_search_fields = [
        "text.string",
    ]

    # Search fields, list is OR
    search_terms = {
    }

    order_by = [("name", "ASC")]

    # Fields for page view; width sum = 95%:
    select_fields = [
        ("name", 45),
        ("color", 20),
        ("priority", 10),
        ("change", 20),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

    def describe(self):
        return self.instance.name

    def delete(self):
        tag_handle = self.instance.handle
        with DbTxn(self._("Delete tag"), self.database) as transaction:
            for (item, handle) in self.database.find_backlink_handles(tag_handle):
                handle_func = self.database.get_table_func(item, "handle_func")
                commit_func = self.database.get_table_func(item, "commit_func")
                obj = handle_func(handle)
                obj.remove_handle_references('Tag', [tag_handle])
                commit_func(obj, transaction)
            self.database.remove_tag(self.instance.handle, transaction)
        self.handler.send_message("Deleted tag. <a href='FIXME'>Undo</a>.")
        self.handler.redirect(self.handler.app.make_url("/tag"))
