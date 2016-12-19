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

from gprime.lib import Person, Surname
from gprime.utils.id import create_id

import tornado.web

from .handlers import BaseHandler
from ..forms import PersonForm

class PersonHandler(BaseHandler):
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
                person = Person()
                person.primary_name.surname_list.append(Surname())
                action = "edit"
            else:
                person = self.database.get_person_from_handle(handle)
            if person:
                person.probably_alive = True
                self.render("person.html",
                            **self.get_template_dict(tview=self._("person detail"),
                                                     action=action,
                                                     page=page,
                                                     search=search,
                                                     form=PersonForm(self.database, self._, instance=person),
                                                     logform=None))
                return
            else:
                self.clear()
                self.set_status(404)
                self.finish("<html><body>No such person</body></html>")
                return
        self.render("page_view.html",
                    **self.get_template_dict(tview=self._("person view"),
                                             page=page,
                                             search=search,
                                             form=PersonForm(self.database, self._),
                                         )
                )

    @tornado.web.authenticated
    def post(self, path):
        if "/" in path:
            handle, action = path.split("/")
        else:
            handle, action = path, "view"
        if handle == "add":
            person = Person()
            person.primary_name.surname_list.append(Surname())
            person.handle = handle = create_id()
        else:
            person = self.database.get_person_from_handle(handle)
        form = PersonForm(self.database, self._, instance=person)
        form.save(handler=self)
        self.redirect("/person/%(handle)s" % {"handle": handle})

