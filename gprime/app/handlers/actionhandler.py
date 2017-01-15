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

from .handlers import BaseHandler
from ..forms.actionform import ActionForm, Action, Table

import tornado.web

class ActionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        HANDLE
        HANDLE/edit|delete
        /add
        b2cfa6ca1e174b1f63d/remove/eventref/1
        """
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1) or 1)
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action= path.split("/", 1)
        else:
            handle, action = path, "view"
        # We don't need connections to other things
        # and will in fact add a new Table:
        if handle:
            table = Table()
            action = table.get_item_by_handle(handle)
            self.render("action.html",
                        **self.get_template_dict(tview=_("action detail"),
                                                 page=page,
                                                 search=search,
                                                 form=ActionForm(self, instance=action),
                                             )
                    )
        else:
            form = ActionForm(self)
            try:
                form.select(page, search)
            except Exception as exp:
                self.send_message(str(exp))
                self.redirect(form.make_url())
                return
            self.render("page_view.html",
                        **self.get_template_dict(tview=_("action view"),
                                                 page=page,
                                                 search=search,
                                                 form=form,
                                             )
                    )

    @tornado.web.authenticated
    def post(self, handle):
        _ = self.app.get_translate_func(self.current_user)
        # Use dict db for place to put Action Table:
        table = Table()
        action = table.get_item_by_handle(handle)
        form = ActionForm(self, instance=action)
        # Run report on actual database:
        form.run_action(action, self)
