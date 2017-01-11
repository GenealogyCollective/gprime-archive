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

from gprime.lib import Person, Surname
from gprime.utils.id import create_id

import tornado.web
import json
import html

from .handlers import BaseHandler
from ..forms import PersonForm

class PersonHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, path=""):
        """
        person
        person/add
        person/b2cfa6ca1e174b1f63
        person/b2cfa6ca1e174b1f63/edit
        person/b2cfa6ca1e174b1f63/delete
        """
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1))
        search = self.get_argument("search", "")
        if path.count("/") == 0: # handle
            handle, action = path, "view"
        elif path.count("/") == 1: # handle/add
            handle, action = path.split("/", 1)
        else:
            self.clear()
            self.set_status(404)
            self.finish("<html><body>No such person</body></html>")
            return
        if handle:
            if handle == "add":
                person = Person()
                person.primary_name.surname_list.append(Surname())
                action = "edit"
            else:
                person = self.database.get_person_from_handle(handle)
            if person:
                if action == "delete":
                    ## Delete person
                    form = PersonForm(self, instance=person)
                    form.delete()
                    return
                else:
                    ## Action can be edit or view
                    self.render("person.html",
                            **self.get_template_dict(tview=_("person detail"),
                                                     action=action,
                                                     page=page,
                                                     search=search,
                                                     form=PersonForm(self, instance=person)))
                return
            else:
                self.clear()
                self.set_status(404)
                self.finish("<html><body>No such person</body></html>")
                return
        form = PersonForm(self)
        # Do this here, to catch errors:
        try:
            form.select(page, search)
        except Exception as exp:
            self.send_message(str(exp))
            self.redirect(form.make_url())
            return
        # If no errors, carry on:
        self.render("page_view.html",
                    **self.get_template_dict(tview=_("person view"),
                                             page=page,
                                             search=search,
                                             form=form,
                    )
        )

    @tornado.web.authenticated
    def post(self, path):
        """
        """
        _ = self.app.get_translate_func(self.current_user)
        page = int(self.get_argument("page", 1) or 1)
        search = self.get_argument("search", "")
        if path.count("/") == 0: # handle
            handle, action = path, "view"
        elif path.count("/") == 1: # handle/add
            handle, action = path.split("/", 1)
        else:
            self.clear()
            self.set_status(404)
            self.finish("<html><body>No such person</body></html>")
            return
        json_data = json.loads(html.unescape(self.get_argument("json_data")))
        instance = Person.from_struct(json_data)
        update_json = self.get_argument("update_json", None)
        if update_json:
            # edit the instance
            self.update_instance(instance, update_json)
            form = PersonForm(self, instance=instance)
            form.load_data()
            self.render("person.html",
                        **self.get_template_dict(tview=_("person detail"),
                                                 action=action,
                                                 page=page,
                                                 search=search,
                                                 form=form))
        else:
            self.send_message("Updated person. <a href=\"FIXME\">Undo</a>")
            form = PersonForm(self, instance=instance)
            form.save()
            self.redirect(self.app.make_url("/person/%(handle)s" % {"handle": handle}))
