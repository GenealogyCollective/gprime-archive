#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
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

# gPrime imports:
from gprime.plugins.lib.libhtml import Html
from gprime.lib import *
from gprime.lib.struct import Struct
from gprime.display.name import NameDisplay
from gprime.datehandler import displayer

# Python imports:
import tornado.log

# Globals and functions:
TAB_HEIGHT = 200
name_display = NameDisplay().display
date_display = displayer.display

def nbsp(string):
    """
    """
    if string:
        return string
    else:
        return "&nbsp;"

class Table(object):
    """
    >>> table = Table(form)
    >>> table = Table(form, nested_url, style)
    >>> table.set_columns(("Col1", 10), ("Col2", 90))
    >>> table.append_row("1", "2", "3", goto=goto_url, edit=edit_url)
    >>> table.append_row("4", "5", "6")
    >>> table.get_html("edit")
    """
    def __init__(self, form, style=None):
        self.id = "tab_table" ## css id
        self.obj_type = form.view
        self.handle = form.instance.handle
        self.style = style
        self.form = form
        self.column_widths = None
        self.columns = []
        self.rows = []
        self.gotos = []
        self.edits = []

    def goto_url(self, position):
        return self.gotos[position]

    def edit_url(self, position, *args):
        edit = self.edits[position]
        if args:
            return edit + "/" + ("/".join(args))
        else:
            return edit

    def set_columns(self, *args):
        self.columns = args

    def append_row(self, *args, goto=None, edit=None):
        """
        args = the values for the columns
        goto = the link to goto when click on row
        edit = the link to edit when del,up,down row
        """
        self.rows.append(list(map(nbsp, args)))
        self.gotos.append(goto)
        if edit: # not the same as goto
            self.edits.append(edit)
        else:
            self.edits.append(goto)

    def get_html(self, action, style=None, tab_height=200):
        style = style if style else self.style
        ## Hack of levels of nbsp
        html = Html('div',
                    class_="content",
                    id=self.id,
                    style=("overflow: auto; height:%spx; background-color: #f4f0ec;" %
                           tab_height) if not style else style)
        table = Html("table", width="95%", cellspacing="0")
        rowhtml = Html("tr")
        for (name, width) in self.columns:
            cell = Html("th", class_="TableHeaderCell", width=("%s%%" % width), colspan="1")
            cell += self.form._(name)
            rowhtml += cell
        table += rowhtml

        row_count = 1
        for row in self.rows:
            rowhtml = Html("tr")
            cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[0][1]), colspan="1")
            div = Html("div", style="background-color: lightgray; padding: 2px 0px 0px 2px")
            if action != "edit":
                disabled = "disabled"
            else:
                disabled = ""
            url = self.edit_url(row_count - 1)
            img_remove = self.form.handler.app.make_url("/images/gtk-remove.png")
            img_up = self.form.handler.app.make_url("/images/up.png")
            img_down = self.form.handler.app.make_url("/images/down.png")
            div += """<input type="submit"
name="update_json"
value="%s/remove"
style="background:url(%s) no-repeat; font-size:0; width: 30px; height: 30px;" %s/>""" % (url, img_remove, disabled)
            div += """<input type="submit"
name="update_json"
value="%s/up"
style="background:url(%s) no-repeat; font-size:0; width: 30px; height: 30px;" %s/>""" % (url, img_up, disabled)
            div += """<input type="submit"
name="update_json"
value="%s/down"
style="background:url(%s) no-repeat; font-size:0; width: 30px; height: 30px;" %s/>""" % (url, img_down, disabled)
            cell += div
            rowhtml += cell
            for count in range(1, len(self.columns)):
                cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[count][1]), colspan="1", style="vertical-align: middle")
                cell += """<a href="%s" style="display: block;">%s</a>""" % (self.goto_url(row_count - 1), row[count - 1])
                rowhtml += cell
            table += rowhtml
            row_count += 1
        html += table
        return str(html) #.replace("&amp;nbsp;", "&nbsp;")

#TODO: Ensure user and privacy levels are accounted for in tables
def event_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-events"
    table = Table(form) # form, link-name
    event = Event()
    eventref = EventRef()
    table.set_columns(
        ("", 11),
        (event.get_label("description", form._), 19),
        (event.get_label("type", form._), 10),
        (event.get_label("gid", form._),11),
        (event.get_label("date", form._), 20),
        (event.get_label("place", form._), 19),
        (eventref.get_label("role", form._), 10),
    )
    s = Struct.wrap(form.instance, form.database)
    count = 1
    for event_ref in s.event_ref_list: # eventrefs
        event = event_ref.ref
        table.append_row(event.description,
                         event.type.string,
                         event.gid,
                         event.date.text,
                         event.place.name.value,
                         event_ref.role.string,
                         edit="event_ref_list/%s" % (count),
                         goto=form.make_url("event_ref_list", count))
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px"/>"""
    if action == "view":
        retval += form.make_icon_button(
            form._("Add New Event"),
            "/%s/%s/event_ref_list/add" % (form.view, form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Event"),
            "/%s/%s/event_ref_list/share" % (form.view, form.instance.handle),
            icon="p")
    else:
        retval += """&nbsp;""" # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def name_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-names"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Name"), 29),
        (form._("Type"), 20),
        (form._("Group As"), 15),
        (form._("Source"), 10),
        (form._("Note"), 15),
    )
    if user or form.instance.public:
        count = 0
        for name in [form.instance.primary_name] + form.instance.alternate_names:
            citations = []
            for citation_handle in name.citation_list:
                citation = form.database.get_citation_from_handle(citation_handle)
                if citation:
                    citations.append(citation)
            citationq = len(citations) > 0
            note_text = ""
            for note_handle in name.note_list:
                note = form.database.get_note_from_handle(note_handle)
                if note:
                    note_text = note.text.string[:50]
                    break
            table.append_row(render_name(name),
                             str(name.type) + ["", " " + form._("(preferred)")][int(count == 0)],
                             name.group_as,
                             [form._("No"), form._("Yes")][citationq],
                             note_text,
                             edit="name/%s" % (count),
                             goto=form.make_url("name", (count + 1)))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Name"),
            "/%s/%s/name/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def surname_table(form, user, action, name_row):
    retval = ""
    has_data = False
    cssid = "tab-surnames"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Surname"), 40),
        (form._("prefix"), 39),
        (form._("primary"), 10),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Surname"),
            "/person/%s/name/%s/surname/add" % (form.instance.handle, name_row),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    count = 1
    if user or form.instance.public:
        for surname in form.instance.primary_name.surname_list:
            table.append_row(
                surname.surname,
                surname.prefix,
                surname.primary,
                goto=form.handler.app.make_url("/person/%s/name/%s/surname/%s" % (form.instance.handle, name_row, count)))
            has_data = True
            count += 1
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def enclosed_by_table(form, user, action, placeref_list):
    cssid = "tab-enclosed-by"
    retval = ""
    has_data = False
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("ID"), 10),
        (form._("Name"), 30),
        (form._("Type"), 19),
        (form._("Date"), 30),
    )
    if user or form.instance.public:
        count = 1
        for ref in placeref_list:
            place = form.database.get_place_from_handle(ref.ref)
            table.append_row(place.gid,
                             place.name.value,
                             place.place_type,
                             ref.date,
                             goto=form.make_url("placeref_list", count),
                             edit="placeref_list/%s" % (count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Enclosing Place"),
            "/place/%s/placeref_list/add" % form.instance.handle,
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Enclosing Place"),
            "/place/%s/placeref_list/share" % form.instance.handle,
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def alt_name_table(form, user, action, alt_names):
    cssid = "tab-alt-names"
    retval = ""
    has_data = False
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Name"), 30),
        (form._("Date"), 30),
        (form._("Language"), 29),
    )
    if user or form.instance.public:
        count = 1
        for place_name in alt_names:
            table.append_row(place_name.value,
                             place_name.date,
                             place_name.lang,
                             goto=form.make_url("alt_names", count),
                             edit="alt_names/%s" % (count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Alternate Name"),
            "/%s/%s/alternate_names/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval


def citation_table(form, user, action, citation_list, path=""):
    # FIXME: how can citation_table and source_table both be on same
    # page? This causes problems with form names, tab names, etc.
    retval = ""
    has_data = False
    cssid = "tab-citations"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("ID"), 10),
        (form._("Confidence"), 49),
        (form._("Page"), 30),
    )
    if user or form.instance.public:
        count = 1
        for citation_ref in citation_list:
            if citation_ref:
                citation = form.database.get_citation_from_handle(citation_ref)
                table.append_row(citation.gid,
                                 citation.confidence,
                                 citation.page,
                                 goto=form.handler.app.make_url(citation.make_url()),
                                 edit="%scitation_list/%s" % (path, count))
                has_data = True
                count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Citation"),
            "/%s/%s/citation_list/add" % (form.view, form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Citation"),
            "/%s/%s/citation_list/share" % (form.view, form.instance.handle),
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def repository_table(form, user, action, reporef_list):
    retval = ""
    has_data = False
    cssid = "tab-repositories"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("ID"), 11),
        (form._("Title"), 38),
        (form._("Call number"), 20),
        (form._("Type"), 20),
    )
    if user or form.instance.public:
        count = 1
        for repo_ref in reporef_list:
            handle = repo_ref.ref
            repo = form.database.get_repository_from_handle(handle)
            table.append_row(repo.gid,
                             repo.name,
                             repo_ref.call_number,
                             repo.type,
                             goto=form.make_url("reporef_list/%s" % count),
                             edit="reporef_list/%s" % count)
            has_data = True
            count += 1;
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Repository"),
            "/%s/%s/reporef_list/add" % (form.view, form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Repository"),
            "/%s/%s/reporef_list/share" % (form.view, form.instance.handle),
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def note_table(form, user, action, note_list, path=""):
    retval = ""
    has_data = False
    cssid = "tab-notes"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("ID"), 10),
        (form._("Type"), 20),
        (form._("Note"), 59),
    )
    if user or form.instance.public:
        count = 1
        for handle in note_list:
            note = form.database.get_note_from_handle(handle)
            table.append_row(note.gid,
                             str(note.type.string),
                             note.text.string[:50],
                             goto=form.handler.app.make_url(note.make_url()),
                             edit="%snote_list/%s" % (path, count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Note"),
            "/%s/%s/note_list/add" % (form.view, form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Note"),
            "/%s/%s/note_list/add" % (form.view, form.instance.handle),
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def attribute_table(form, user, action, attribute_list, path=""):
    retval = ""
    has_data = False
    cssid = "tab-attributes"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Type"), 40),
        (form._("Value"), 49),
    )
    count = 1
    url = path.replace(".", "/")
    if user or form.instance.public:
        for attribute in attribute_list:
            table.append_row(attribute.type.string,
                             attribute.value,
                             edit="%sattribute_list/%s" % (path, count),
                             goto=form.make_url("attribute_list", count))
            count += 1
            has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Attribute"),
            "/%s/%s/%sattribute_list/add" % (form.view, form.instance.handle, url),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def address_table(form, user, action, address_list):
    retval = ""
    has_data = False
    cssid = "tab-addresses"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Date"), 15),
        (form._("Address"), 29),
        (form._("City"), 15),
        (form._("State"), 15),
        (form._("Country"), 15),
    )
    count = 1
    for address in address_list:
        table.append_row(address.date.text,
                         address.street,
                         address.city,
                         address.state,
                         address.country,
                         edit="address_list/%s" % count,
                         goto=form.make_url("address_list", count))
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Address"),
            "/%s/%s/address_list/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def media_table(form, user, action, media_list):
    retval = ""
    has_data = False
    cssid = "tab-media"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Description"), 49),
        (form._("Type"), 10),
        (form._("Path/Filename"), 30),
    )
    count = 1
    if user or form.instance.public:
        for media_ref in media_list:
            media = form.database.get_media_from_handle(media_ref.ref)
            table.append_row(media.desc,
                             media.mime,
                             media.path,
                             goto=form.make_url("media_list", count),
                             edit="media_list/%s" % (count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Media"),
            "/%s/%s/media_list/add" % (form.view, form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Share Existing Media"),
            "/%s/%s/media_list/share" % (form.view, form.instance.handle),
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def internet_table(form, user, action, urls):
    retval = ""
    has_data = False
    cssid = "tab-internet"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Type"), 19),
        (form._("Path"), 35),
        (form._("Description"), 35),
    )
    count = 1
    for url in urls:
        table.append_row(url.type.string,
                         url.path,
                         url.desc,
                         edit="urls/%s" % count,
                         goto=form.make_url("urls", count))
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Internet"),
            "/%s/%s/urls/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def association_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-association"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Name"), 40),
        (form._("ID"), 10),
        (form._("Association"), 39),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Association"),
            "/%s/%s/person_ref_list/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    if user or form.instance.public:
        s = Struct.wrap(form.instance, form.database)
        count = 1
        for personref in s.person_ref_list:
            table.append_row(
                name_display(personref.ref.instance),
                personref.ref.gid,
                personref.rel,
                edit="person_ref_list/%s" % count,
                goto=form.make_url("person_ref_list", count))
            has_data = True
            count += 1
        text = """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
        text += """</div>"""
        text += table.get_html(action)
        retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def location_table(form, user, action):
    # obj is Place or Address
    retval = ""
    has_data = False
    cssid = "tab-alternatelocations"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Street"), 10),
        (form._("Locality"), 10),
        (form._("City"), 10),
        (form._("State"), 10),
        (form._("Country"), 10),
    )
    if user or form.instance.public:
        # FIXME: location confusion!
        # The single Location on the Location Tab is here too?
        # I think if Parish is None, then these are single Locations;
        # else they are in the table of alternate locations
        # could be: place.alt_loc, address.location, researcher
        count = 1
        for location in form.instance.alt_loc:
            table.append_row(
                location.street,
                location.locality,
                location.city,
                location.state,
                location.country,
                goto=form.make_url("address_list", count),
                edit="address_list/%s" % count)
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add Address"),
            "/%s/%s/address_list/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def lds_table(form, user, action, lds_ord_list):
    retval = ""
    has_data = False
    cssid = "tab-lds"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Type"), 10),
        (form._("Date"), 19),
        (form._("Status"), 10),
        (form._("Temple"), 20),
        (form._("Place"), 30),
    )
    count = 1
    if user or form.instance.public:
        for lds in lds_ord_list:
            date = lds.date
            table.append_row(lds.type,
                             date_display(date) if date else "",
                             lds.status,
                             lds.temple,
                             lds.place.title,
                             edit="lds_ord_list/%s" % count,
                             goto=form.make_url("lds_ord_list", count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add LDS"),
            "/%s/%s/lds_ord_list/add" % (form.view, form.instance.handle),
            icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def person_reference_table(form, user, action):
    from gprime.simple import SimpleAccess
    sa = SimpleAccess(form.database)
    retval = ""
    has_data = False
    cssid = "tab-references"
    text1 = ""
    text2 = ""
    table1 = Table(form, style="background-color: #f4f0ec;")
    table1.set_columns(
        (form._("As Spouse"), 11),
        (form._("ID"), 10),
        (form._("Reference"), 79),
    )
    table2 = Table(form, style="background-color: #f4f0ec;")
    table2.set_columns(
        (form._("As Child"), 11),
        (form._("ID"), 10),
        (form._("Reference"), 79),
    )
    if (user or form.instance.public) and action != "add":
        s = Struct.wrap(form.instance, form.database)
        count = 1
        for family in s.family_list:
            table1.append_row(family.gid,
                              sa.describe(family.instance),
                              goto=form.handler.app.make_url(family.instance.make_url()),
                              edit="family_list/%s" % count)
            has_data = True
            count += 1
        count = 1
        for family in s.parent_family_list:
            table2.append_row(family.gid,
                              sa.describe(family.instance),
                              goto=form.handler.app.make_url(family.instance.make_url()),
                              edit="parent_family_list/%s" % count)
            has_data = True
            count += 1
        text1 = """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
        if user and action == "view":
            text1 += form.make_icon_button(form._("Add as Spouse to New Family"),
                                      "/family/%s/parent_family_list/add" % (form.instance.handle),
                                      icon="+")
            text1 += form.make_icon_button(form._("Add as Spouse to Existing Family"),
                                      "/family/%s/parent_family_list/share" % (form.instance.handle),
                                      icon="p")
        else:
            text1 += nbsp("") # to keep tabs same height
        text1 += """</div>"""
        text1 += table1.get_html(action, tab_height="100%")
        text2 = """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
        if user and action == "view":
            text2 += form.make_icon_button(form._("Add as Child to New Family"),
                                      "/family/%s/family_list/add" % (form.instance.handle),
                                      icon="+")
            text2 += form.make_icon_button(form._("Add as Child to Existing Family"),
                                      "/family/%s/family_list/share" % (form.instance.handle),
                                      icon="p")
        else:
            text2 += nbsp("") # to keep tabs same height
        text2 += """</div>"""
        text2 += table2.get_html(action, tab_height="100%")

    retval += """<div style="overflow: auto; height:%spx;">""" % TAB_HEIGHT
    retval += text1 + text2
    retval += "</div>"
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def reference_table(form, user, action):
    from gprime.simple import SimpleAccess
    sa = SimpleAccess(form.database)
    retval = ""
    has_data = False
    count = 0;
    cssid = "tab-references"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Type"), 10),
        (form._("Reference"), 69),
        (form._("ID"), 10),
        )
    for ref_pair in form.database.find_backlink_handles(form.instance.handle):
        obj_type, handle = ref_pair
        obj = form.database.get_table_func(obj_type, "handle_func")(handle)
        table.append_row(obj_type, sa.describe(obj), obj.gid,
                         goto=form.handler.app.make_url(obj.make_url()),
                         edit=None)
        has_data = True
    retval += table.get_html(action)
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def children_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-children"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("#"), 5),
        (form._("ID"), 10),
        (form._("Name"), 29),
        (form._("Gender"), 8),
        (form._("Paternal"), 8),
        (form._("Maternal"), 10),
        (form._("Birth Date"), 19),
    )
    count = 1
    for childref in form.instance.child_ref_list:
        handle = childref.ref
        child = form.database.get_person_from_handle(handle)
        table.append_row(str(count),
                         "[%s]" % child.gid,
                         name_display(child),
                         render_gender(child.gender),
                         childref.frel.string,
                         childref.mrel.string,
                         form.birth_date(child),
                         goto=form.make_url("child_ref_list", count),
                         edit="child_ref_list/%s" % count)
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px"/>"""
    if user and action == "view":
        retval += form.make_icon_button(
            form._("Add New Child"),
            "/family/%s/child_ref_list/add" % (form.instance.handle),
            icon="+")
        retval += form.make_icon_button(
            form._("Add Existing Person as Child"),
            "/family/%s/child_ref_list/share" % (form.instance.handle),
            icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += "</div>"
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def render_name(name):
    """
    Given a Gramps object, render the name and return.  This
    function uses authentication, privacy and probably_alive settings.
    """
    if name is None:
        return "[no name]"
    if len(name.surname_list) > 0:
        surname = name.surname_list[0].surname
    else:
        surname = "[No primary surname]"
    return "%s, %s" % (surname, name.first_name)

def render_gender(gender):
    return {2: "unknown",
            1: "male",
            0: "female"}[gender]

def render_css(form, user, action):
    css_list = [ "Web_Basic-Ash.css",
                 "Web_Basic-Blue.css",
                 "Web_Basic-Cypress.css",
                 "Web_Basic-Lilac.css",
                 "Web_Basic-Peach.css",
                 "Web_Basic-Spruce.css",
                 "Web_Mainz.css",
                 "Web_Nebraska.css",
                 "Web_Print-Default.css",
                 "Web_Visually.css"]
    default = form.database.get_user_data(user)
    retval = """<select name="css">"""
    for css in sorted(css_list):
        selected = "selected" if default["css"] == css else ""
        retval += """<option value="%s" %s>%s</option>""" % (css, selected, css)
    retval += "</select>"
    return retval

def render_language(form, user, action):
    languages = [
        ('ar', "Arabic", form._("Arabic")),
        ('bg', "Bulgarian", form._("Bulgarian")),
        ('ca', "Catalan", form._("Catalan")),
        ('cs', "Czech", form._("Czech")),
        ('da', "Danish", form._("Danish")),
        ('de', "German", form._("German")),
        ('el', "Greek", form._("Greek")),
        ('en', "English", form._("English")),
        ('en_GB', "English, Great Britian", form._("English, Great Britian")),
        ('eo', "Esperanto", form._("Esperanto")),
        ('es', "Spanish", form._("Spanish")),
        ('fi', "Finnish", form._("Finnish")),
        ('fr', "French", form._("French")),
        ('he', "Hebrew", form._("Hebrew")),
        ('hr', "Croatian", form._("Croatian")),
        ('hu', "Hungarian", form._("Hungarian")),
        ('is', "Icelandic", form._("Icelandic")),
        ('it', "Italian", form._("Italian")),
        ('ja', "Japanese", form._("Japanese")),
        ('lt', "Lithuanian", form._("Lithuanian")),
        ('nb', "Norwegian Bokmål", form._("Norwegian Bokmål")),
        ('nl', "Dutch", form._("Dutch")),
        ('nn', "Norwegian Nynorsk", form._("Norwegian Nynorsk")),
        ('pl', "Polish", form._("Polish")),
        ('pt_BR', "Portuguese, Brazil", form._("Portuguese, Brazil")),
        ('pt_PT', "Portuguese, Portugal", form._("Portuguese, Portugal")),
        ('ru', "Russian", form._("Russian")),
        ('sk', "Slovak", form._("Slovak")),
        ('sl', "Slovenian", form._("Slovenian")),
        ('sq', "Albanian", form._("Albanian")),
        ('sr', "Serbian", form._("Serbian")),
        ('sv', "Swedish", form._("Swedish")),
        ('tr', "Turkish", form._("Turkish")),
        ('uk', "Ukrainian", form._("Ukrainian")),
        ('vi', "Vietnamese", form._("Vietnamese")),
        ('zh_CN', "Chinese, mainland China", form._("Chinese, mainland China")),
        ('zh_HK', "Chinese, Hong Kong", form._("Chinese, Hong Kong")),
        ('zh_TW', "Chinese, Taiwan", form._("Chinese, Taiwan")),
    ]
    default = form.database.get_user_data(user)
    retval = """<select name="language">"""
    for (language, name, tname) in sorted(languages, key=lambda items: items[2]):
        selected = "selected" if default["language"] == language else ""
        if name == tname:
            retval += """<option value="%s" %s>%s</option>""" % (language, selected, name)
        else:
            retval += """<option value="%s" %s>%s (%s)</option>""" % (language, selected, tname, name)
    retval += "</select>"
    return retval
