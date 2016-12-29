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

from passlib.hash import sha256_crypt as crypt

class SettingsForm():
    """
    A form for listing, viewing, and editing user settings.
    """
    def __init__(self, handler, database, _):
        self.database = database
        self.handler = handler
        self._ = _
        self.tview = self._("Settings")
        self.view = "Settings"
        self.instance = self.database.get_user_data(self.handler.current_user)

    def save(self, handler):
        self.handler = handler
        # save the settings to the user table
        update = {}
        for field in ["css", "language", "email", "name"]:
            update[field] = handler.get_argument(field)
        if handler.get_argument("password"):
            update["password"] = crypt.hash(handler.get_argument("password"))
        self.database.update_user_data(handler.current_user, update)
        handler.app.clear_user_data(handler.current_user)
