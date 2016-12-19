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

# Gramps imports:
from gprime.lib.citation import Citation

# Gramps Connect imports:
from .forms import Form

class CitationForm(Form):
    """
    A form for listing, viewing, and editing a Person object.
    """
    _class = Citation
    view = "citation"
    tview = "Citations"
    table = "Citation"

    # Fields for editor:
    edit_fields = [
        "type",
        "text.string",
        "gid",
        "tag_list",
        "private",
    ]

    # URL for page view rows:
    link = "/citation/%(handle)s"

    # Search fields to use if not specified:
    default_search_fields = [
        "text.string",
        "gid",
    ]

    # Search fields, list is OR
    search_terms = {
        "text": "text.string",
        "id": "gid",
    }

    order_by = [("gid", "ASC")]

    # Fields for page view; width sum = 95%:
    select_fields = [
        ("gid", 10),
        ("date", 10),
        ("page", 10),
        ("confidence", 5),
        ("change", 20),
        ("private", 10),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle",
    ]

