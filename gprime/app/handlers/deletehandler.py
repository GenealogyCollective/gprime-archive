#
# Gramps - a GTK+/GNOME based genealogy program
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

import tornado.web

from .handlers import BaseHandler
from ..forms import PersonForm

class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, table, handle):
        handle_func = self.database.get_table_func(table.title(),"handle_func")
        instance = handle_func(handle)
        form_class = self.get_form(table)
        form = form_class(self.database, self._, instance=instance)
        self.render('delete.html',
                    **self.get_template_dict(form=form,
                                             table=table,
                                             handle=handle,
                                             tview="delete"))
    @tornado.web.authenticated
    def post(self, table, handle):
        transaction = self.database.get_transaction_class()
        del_func = self.database.get_table(table.title(),"del_func")
        with transaction("Gramps Connect", self.database) as trans:
            del_func(handle, trans)
        self.redirect("/" + table)
