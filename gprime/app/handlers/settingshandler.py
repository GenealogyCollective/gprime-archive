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
from ..forms import SettingsForm

class SettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        """
        _ = self.app.get_translate_func(self.current_user)
        self.render("settings.html",
                    **self.get_template_dict(tview=_("settings"),
                                             form=SettingsForm(self)))
        return

    @tornado.web.authenticated
    def post(self, path=""):
        _ = self.app.get_translate_func(self.current_user)
        form = SettingsForm(self)
        form.save()
        self.redirect(self.app.make_url("/settings"))
