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

from .forms import Form

class SurnameForm(Form):
    """
    A form for listing, viewing, and editing user settings.
    """
    table = "Person"

    def __init__(self, handler, instance, handle, name_row, surname_row):
        super().__init__(handler, instance)
        self.tview = self._("Surname")
        self.view = "Surname"
        self.name_row = name_row
        self.surname_row = surname_row
        self.handle = handle
        self.edit_fields = []
        if self.name_row == 1:
            for field in [
                    "primary_name.surname_list.%s.surname",
                    "primary_name.surname_list.%s.prefix",
                    "primary_name.surname_list.%s.connector",
                    "primary_name.surname_list.%s.origintype",
                    "primary_name.surname_list.%s.primary",
            ]:
                self.edit_fields.append(field % (int(self.surname_row) - 1))
        else:
            for field in [
                    "alternate_names.%s.surname_list.%s.surname",
                    "alternate_names.%s.surname_list.%s.prefix",
                    "alternate_names.%s.surname_list.%s.connector",
                    "alternate_names.%s.surname_list.%s.origintype",
                    "alternate_names.%s.surname_list.%s.primary",
            ]:
                self.edit_fields.append(field % (int(self.name_row) - 2, int(self.surname_row) - 1))

