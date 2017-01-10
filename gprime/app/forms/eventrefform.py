#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2017 gPrime Development Team
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

# Gramps Connect imports:
from .forms import Form
from gprime.lib.person import Person

class EventRefForm(Form):
    """
    A form for listing, viewing, and editing user settings.
    """
    def __init__(self, handler, instance, subitem, path, url):
        self.set_class_from_url(url, handler)
        super().__init__(handler, instance)
        self.path = path
        self.url = url
        self.subitem = subitem
        self.edit_fields = []
        for field in ["type", "value", "private"]:
            self.edit_fields.append(path + "." + field)
