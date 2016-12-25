#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2016 gPrime Development Team
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

import gprime.const
import os
from passlib.hash import sha256_crypt as crypt

class PasswordManager():
    def __init__(self):
        self.account = {}

    def save(self):
        filename = os.path.join(gprime.const.get_site_dir(), "passwd")
        with open(filename, "w") as fp:
            fp.write("### This is the password file for gPrime\n")
            fp.write("\n")
            for username in self.account:
                fp.write("%s:%s\n" % (username, self.account[username]))

    def load(self):
        filename = os.path.join(gprime.const.get_site_dir(), "passwd")
        self.account.clear()
        for line in open(filename):
            if line.strip():
                if not line.startswith("#"):
                    username, password_hash = [word.strip() for word in line.split(":")]
                    self.account[username] = password_hash

    def add_user(self, username, password):
        if username in self.account:
            raise Exception("Username already exists: %s" % username)
        password_hash = crypt.hash(password)
        self.account[username] = password_hash

    def remove_user(self, username):
        if username in self.account[username]:
            del self.account[username]
        else:
            raise Exception("Username does not exist: %s" % username)

    def change_password(self, username, password):
        password_hash = crypt.hash(password)
        self.account[username] = password_hash

    def verify_password(self, username, password):
        return crypt.verify(password, self.account[username])

password_manager = PasswordManager()
