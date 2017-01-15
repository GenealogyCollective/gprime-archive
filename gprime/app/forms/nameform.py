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

class NameForm(Form):
    """
    A form for listing, viewing, and editing user settings.
    """
    table = "Person"
    def __init__(self, handler, instance, handle, row):
        super().__init__(handler, instance)
        self.tview = self._("Name")
        self.view = "Name"
        self.row = row
        self.handle = handle
        if int(row) == 1:
            self.path = "primary_name"
        else:
            self.path = "alternate_name.%s" % (int(self.row) - 2)
        self.edit_fields = []
        if int(row) == 1:
            for field in [
                    'primary_name.type',
                    'primary_name.first_name',
                    'primary_name.call',
                    'primary_name.nick',
                    'primary_name.famnick',
                    'primary_name.private',
                    'primary_name.date',
                    'primary_name.suffix',
                    'primary_name.title',
                    'primary_name.group_as',
                    'primary_name.sort_as',
                    'primary_name.display_as',
                    ]:
                self.edit_fields.append(field)
        else:
            for field in [
                    'alternate_names.%s.type',
                    'alternate_names.%s.first_name',
                    'alternate_names.%s.call',
                    'alternate_names.%s.nick',
                    'alternate_names.%s.famnick',
                    'alternate_names.%s.private',
                    'alternate_names.%s.date',
                    'alternate_names.%s.suffix',
                    'alternate_names.%s.title',
                    'alternate_names.%s.group_as',
                    'alternate_names.%s.sort_as',
                    'alternate_names.%s.display_as',
                    ]:
                self.edit_fields.append(field % (int(self.row) - 2))
