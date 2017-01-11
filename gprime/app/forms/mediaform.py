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
from gprime.lib.media import Media
from gprime.db import DbTxn

# Gramps Connect imports:
from .forms import Form

class MediaForm(Form):
    """
    A form for listing, viewing, and editing a Person object.
    """
    _class = Media
    view = "media"
    tview = "Media"
    table = "Media"

    # Fields for editor:
    edit_fields = [
        "gid",
        "tag_list",
        "private",
        "desc",
        "date",
        "path",
    ]

    # URL for page view rows:
    link = "/media/%(handle)s"

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
        ("path", 20),
        ("desc", 25),
        ("change", 25),
        ("date", 10),
        ("private", 5),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

    def delete(self):
        media_handle = self.instance.handle
        with DbTxn(self._("Delete media"), self.database) as transaction:
            for (item, handle) in self.database.find_backlink_handles(media_handle):
                handle_func = self.database.get_table_func(item, "handle_func")
                commit_func = self.database.get_table_func(item, "commit_func")
                obj = handle_func(handle)
                obj.remove_handle_references('Media', [media_handle])
                commit_func(obj, transaction)
            self.database.remove_media(self.instance.handle, transaction)
        self.handler.send_message(self._("Deleted media. <a href='%s'>Undo</a>." % "FIXME"))
        self.handler.redirect(self.handler.app.make_url("/media"))
