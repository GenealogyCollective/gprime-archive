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

import tornado.web
import sys
import logging
import hmac
import json
from passlib.hash import sha256_crypt as crypt

from gprime.utils.locale import Locale, _
from gprime.const import VERSION

template_functions = {}
exec("from gprime.app.template_functions import *",
     globals(), template_functions)

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(".Handler")
        self.database = None
        self.sitename = None
        self.opts = None
        for name in ["database", "sitename", "opts", "app"]:
            if name in kwargs:
                setattr(self, name, kwargs[name])
                del kwargs[name]
        super().__init__(*args, **kwargs)

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns['_T_'] = lambda *x: '"{0}"'.format(ns['_'](*x))
        return ns

    def write_error(self, status_code, **kwargs):
        exception_class, exception, tb  = sys.exc_info()
        self.render('error_unknown.html',
                    page=None,
                    **self.get_template_dict(
                        messages=[str(exception)]
                    ))

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if isinstance(user, bytes):
            user = user.decode()
        return user

    def get_template_dict(self, **kwargs):
        dict = {
            "database": self.database,
            "menu": [],
            "action": "view",
            "user": self.current_user,
            "sitename": self.sitename,
            "opts": self.opts,
            "css_theme": self.app.get_css(self.current_user),
            "_": self.app.get_translate_func(self.current_user),
            "gprime_version": VERSION,
            "messages": self.get_messages(),
            "next": self.get_argument("next", None),
            "make_url": self.make_url
        }
        dict.update(template_functions)
        dict.update(kwargs)
        return dict

    def make_url(self, url):
        return self.app.make_url(url)

    def send_message(self, message):
        self.set_secure_cookie("gprime-messages",
                               json.dumps([message]).encode())

    def get_messages(self):
        # get cookie values:
        cookie = self.get_secure_cookie("gprime-messages")
        retval = []
        if cookie:
            retval = json.loads(cookie.decode())
            self.clear_cookie("gprime-messages")
        return retval

    def get_form(self, table):
        """
        Return the proper form, give a table name.
        """
        from ..forms import PersonForm, FamilyForm
        if table == "person":
            form = PersonForm
        elif table == "family":
            form = FamilyForm
        else:
            raise Exception("invalid form")
        return form

    def update_instance(self, instance, update_json):
        path, pos, command = update_json.split("/")
        pos = int(pos) - 1 # URLs are 1-based
        list = instance.get_field(path)
        if command == "remove":
            del list[pos]
        elif command == "up":
            list[pos], list[pos + 1] = list[pos + 1], list[pos]
        elif command == "down":
            list[pos], list[pos - 1] = list[pos - 1], list[pos]
        else:
            raise Exception("invalid command: %s" % command)

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('home.html', **self.get_template_dict())

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html',
                    **self.get_template_dict())
    def post(self):
        getusername = self.get_argument("username")
        getpassword = self.get_argument("password")
        user_data = self.database.get_user_data(getusername)
        if user_data and user_data["password"] and crypt.verify(getpassword, user_data["password"]):
            self.set_secure_cookie("user", self.get_argument("username"))
            self.redirect(self.get_argument("next",
                                            self.reverse_url("main")))
        else:
            self.redirect(self.reverse_url("login"))

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next",
                                        self.reverse_url("main")))

class My404Handler(BaseHandler):
    # Override prepare() instead of get() to cover all possible HTTP methods.
    def prepare(self):
        self.render('error_404.html',
                    page=None,
                    **self.get_template_dict(
                        messages=["Page cannot be located."]
                    ))
