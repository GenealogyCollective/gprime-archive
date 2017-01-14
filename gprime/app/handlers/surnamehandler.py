#
# gPrime - a web-based genealogy program
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

import tornado.web

from .handlers import BaseHandler
from ..forms import SurnameForm
from gprime.lib.surname import Surname

class SurnameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, handle, name_row, surname_row):
        """
        """
        if "/" in surname_row:
            surname_row, action = surname_row.split("/")
        else:
            action = "view"
        if surname_row == "add":
            pass # FIXME
        elif surname_row == "delete":
            pass # FIXME
        else:
            name_row = int(name_row)
            surname_row = int(surname_row)
        _ = self.app.get_translate_func(self.current_user)
        instance = self.database.get_person_from_handle(handle)
        self.render("surname.html",
                    **self.get_template_dict(tview=_("surname"),
                                             action=action,
                                             form=SurnameForm(self, instance, handle, name_row, surname_row)))
        return

    @tornado.web.authenticated
    def post(self, handle, name_row, surname_row):
        if "/" in surname_row:
            surname_row, action = surname_row.split("/")
        else:
            action = "view"
        if surname_row == "add":
            pass # FIXME
        elif surname_row == "delete":
            pass # FIXME
        else:
            name_row = int(name_row)
            surname_row = int(surname_row)
        _ = self.app.get_translate_func(self.current_user)
        ## FIXME: handle post to remove/up/down names (primary name is listed)
        instance = self.database.get_person_from_handle(handle)
        form = SurnameForm(self, instance, handle, name_row, surname_row)
        form.save()
        self.redirect(self.app.make_url(instance.make_url("name", name_row, "#tab-surnames")))
