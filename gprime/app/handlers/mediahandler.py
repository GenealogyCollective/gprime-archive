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

from gprime.lib import Media
from gprime.utils.id import create_id

import tornado.web
import json
import html

from .handlers import BaseHandler
from ..forms import MediaForm

class MediaHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        HANDLE
        HANDLE/edit|delete
        /add
        b2cfa6ca1e174b1f63d/remove/eventref/1
        """
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1))
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action= path.split("/", 1)
        else:
            handle, action = path, "view"
        if handle:
            if handle == "add":
                media = Media()
                action = "edit"
            else:
                media = self.database.get_media_from_handle(handle)
            if media:
                if action == "delete":
                    form = MediaForm(self, instance=media)
                    form.delete()
                    return
                else:
                    self.render("media.html",
                                **self.get_template_dict(tview=_("media detail"),
                                                         action=action,
                                                         page=page,
                                                         search=search,
                                                         form=MediaForm(self, instance=media)))
                    return
            else:
                self.clear()
                self.set_status(404)
                self.finish("<html><body>No such media</body></html>")
                return
        form = MediaForm(self)
        try:
            form.select(page, search)
        except Exception as exp:
            self.send_message(str(exp))
            self.redirect(form.make_url())
            return
        self.render("page_view.html",
                    **self.get_template_dict(tview=_("media view"),
                                             page=page,
                                             search=search,
                                             form=form,
                                         )
                )

    @tornado.web.authenticated
    def post(self, path):
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1) or 1)
        search = self.get_argument("search", "")
        if "/" in path:
            handle, action = path.split("/")
        else:
            handle, action = path, "view"
        json_data = json.loads(html.unescape(self.get_argument("json_data")))
        instance = Media.from_struct(json_data)
        update_json = self.get_argument("update_json", None)
        if update_json:
            # edit the instance
            self.update_instance(instance, update_json)
            form = MediaForm(self, instance=instance)
            form.load_data()
            self.render("media.html",
                        **self.get_template_dict(tview=_("media detail"),
                                                 action=action,
                                                 page=page,
                                                 search=search,
                                                 form=form))
        else:
            self.send_message("Updated media. <a href=\"FIXME\">Undo</a>")
            form = MediaForm(self, instance=instance)
            form.save()
            self.redirect(self.app.make_url("/media/%(handle)s" % {"handle": handle}))

