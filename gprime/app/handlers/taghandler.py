#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2015-2016 Gramps Development Team
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

from gprime.lib import Tag
from gprime.utils.id import create_id

import tornado.web

from .handlers import BaseHandler
from ..forms import TagForm

class TagHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        HANDLE
        HANDLE/edit|delete
        /add
        b2cfa6ca1e174b1f63d/remove/eventref/1
        """
        page = int(self.get_argument("page", 1))
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action= path.split("/", 1)
        else:
            handle, action = path, "view"
        if handle:
            if handle == "add":
                tag = Tag()
                action = "edit"
            else:
                tag = self.database.get_tag_from_handle(handle)
            if tag:
                self.render("tag.html",
                            **self.get_template_dict(tview=self._("tag detail"),
                                                     action=action,
                                                     page=page,
                                                     search=search,
                                                     form=TagForm(self.database, self._, instance=tag),
                                                     logform=None))
                return
            else:
                self.clear()
                self.set_status(404)
                self.finish("<html><body>No such tag</body></html>")
                return
        self.render("page_view.html",
                    **self.get_template_dict(tview=self._("tag view"),
                                             page=page,
                                             search=search,
                                             form=TagForm(self.database, self._),
                                         )
                )

    @tornado.web.authenticated
    def post(self, path):
        if "/" in path:
            handle, action = path.split("/")
        else:
            handle, action = path, "view"
        if handle == "add":
            tag = Tag()
            tag.handle = handle = create_id()
        else:
            tag = self.database.get_tag_from_handle(handle)
        form = TagForm(self.database, self._, instance=tag)
        form.save(handler=self)
        self.redirect("/tag/%(handle)s" % {"handle": handle})

