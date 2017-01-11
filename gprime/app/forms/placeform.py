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
from gprime.lib.place import Place
from gprime.db import DbTxn

# Gramps Connect imports:
from .forms import Form

class PlaceForm(Form):
    """
    A form for listing, viewing, and editing a Person object.
    """
    _class = Place
    view = "place"
    tview = "Place"
    table = "Place"

    # Fields for editor:
    edit_fields = [
        "gid",
        "tag_list",
        "private",
        'name.value',
        'name.date',
        'name.lang',
        'lat',
        'long',
        'place_type',
        'code',
    ]

    # URL for page view rows:
    link = "/place/%(handle)s"

    # Search fields to use if not specified:
    default_search_fields = [
        "text.string",
        "gid",
    ]

    # Search fields, list is OR
    search_terms = {
        "text": "text.string",
        "id": "gid",
    }

    order_by = [("gid", "ASC")]

    # Fields for page view; width sum = 95%:
    select_fields = [
        ("gid", 10),
        ("name", 10),
        ("title", 30),
        ("long", 10),
        ("lat", 10),
        ("code", 10),
        ("change", 10),
        ("private", 5),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

    def delete(self):
        place_handle = self.instance.handle
        with DbTxn(self._("Delete place"), self.database) as transaction:
            for (item, handle) in self.database.find_backlink_handles(place_handle):
                handle_func = self.database.get_table_func(item, "handle_func")
                commit_func = self.database.get_table_func(item, "commit_func")
                obj = handle_func(handle)
                obj.remove_handle_references('Place', [place_handle])
                commit_func(obj, transaction)
            self.database.remove_place(place_handle, transaction)
        self.handler.send_message("Deleted place. <a href='FIXME'>Undo</a>.")
        self.handler.redirect(self.handler.app.make_url("/place"))
