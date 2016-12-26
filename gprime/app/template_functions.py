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

def make_button(text, link):
    return """<input type="button" value="%s" onclick="location.href='%s';" />""" % (text, link)

def make_icon_button(text, link, **kwargs):
    if "icon" in kwargs:
        if kwargs["icon"] == "+":
            img_src = "/images/add.png"
        elif kwargs["icon"] == "?":
            img_src = "/images/text-editor.png"
        elif kwargs["icon"] == "-":
            img_src = "/images/gtk-remove.png"
        elif kwargs["icon"] == "p": # pick
            img_src = "/images/stock_index_24.png"
        else:
            raise Exception("invalid icon: %s" % kwargs["icon"])
        return ("""<img height="22" width="22" alt="%(text)s" title="%(text)s"
     src="%(img_src)s" onmouseover="buttonOver(this)" onmouseout="buttonOut(this)"
        onclick="document.location.href='%(link)s'"
     style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;" />
""") % {"link": link % kwargs,
        "img_src": img_src,
        "text": text}
    else:
        return """<a href="%(link)s" class="browsecell">%(text)s</a>""" % {"link": link % kwargs,
                                                       "text": text}

def make_link(url, text, **kwargs):
    return """<a href="%s"><b>%s</b></a>""" % ((url % kwargs), text)

def nbsp(string):
    """
    """
    if string:
        return string
    else:
        return "&nbsp;"

class Table(object):
    """
    >>> table = Table("eventref")
    >>> table.set_columns(("Col1", 10), ("Col2", 90))
    >>> table.append_row("1", "2", "3", link="/person/37463746")
    >>> table.append_row("4", "5", "6", link="/event/3763746")
    >>> table.get_html("edit")
    """
    def __init__(self, form, ttype=None, ttype_obj=None, style=None):
        self.id = "tab_table" ## css id
        self.obj_type = form.view
        self.handle = form.instance.handle
        self.ttype = ttype  # "eventref"
        self.ttype_obj = ttype_obj # "event"
        self.style = style
        self.form = form
        self.column_widths = None
        self.columns = []
        self.rows = []
        self.links = []

    def set_columns(self, *args):
        self.columns = args

    def append_row(self, *args, link=None):
        self.rows.append(list(map(nbsp, args)))
        self.links.append(link)

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
        for row in self.rows: #TODO: Properly implement the remove/up/down buttons
            rowhtml = Html("tr")
            cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[0][1]), colspan="1")
            div = Html("div", style="background-color: lightgray; padding: 2px 0px 0px 2px")
            div += Html("img", height="22", width="22",
                        alt="Delete row", title="Delete row",
                        src="/images/gtk-remove.png",
                        onmouseover="buttonOver(this)" if action == "edit" else None,
                        onmouseout="buttonOut(this)" if action == "edit" else None,
                        onclick="document.location.href='/%s/%s/remove/%s/%s'" % (self.obj_type, self.handle, self.ttype, row_count) if action == "edit" else None,
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            div += Html("img", height="22", width="22",
                        alt="Move row up", title="Move row up",
                        src="/images/up.png",
                        onmouseover="buttonOver(this)" if action == "edit" and row_count > 1 else None,
                        onmouseout="buttonOut(this)" if action == "edit" and row_count > 1 else None,
                        onclick="document.location.href='/%s/%s/up/%s/%s'" % (self.obj_type, self.handle, self.ttype, row_count) if action == "edit" and row_count > 1 else None,
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            div += Html("img", height="22", width="22",
                        alt="Move row down", title="Move row down",
                        src="/images/down.png",
                        onmouseover="buttonOver(this)" if action == "edit" and row_count < len(self.rows) else None,
                        onmouseout="buttonOut(this)" if action == "edit" and row_count < len(self.rows) else None,
                        onclick="document.location.href='/%s/%s/down/%s/%s'" % (self.obj_type, self.handle, self.ttype, row_count) if action == "edit" and row_count < len(self.rows) else None,
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            cell += div
            rowhtml += cell
            for count in range(1, len(self.columns)):
                cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[count][1]), colspan="1")
                url = self.links[row_count - 1]
                try:
                    cell += """<a href="%s" style="display: block;">%s</a>""" % (url, row[count - 1])
                except:
                    tornado.log.logging.info("improper rows: %s", row)
                rowhtml += cell
            table += rowhtml
            row_count += 1
        html += table
        return str(html) #.replace("&amp;nbsp;", "&nbsp;")

#TODO: Ensure user and privacy levels are accounted for in tables
#TODO: Rows in tables should link to objects (or objects should be otherwise editable from tables)
def event_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-events"
    table = Table(form, "eventref", "event")
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
    count = 0
    for event_ref in s.event_ref_list: # eventrefs
        event = event_ref.ref
        table.append_row(event.description,
                         event.type.string,
                         event.gid,
                         event.date.text,
                         event.place.name.value,
                         event_ref.role.string,
                         link="/event/%s" % event.instance.handle)
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px"/>"""
    if action == "view":
        retval += make_icon_button(form._("Add New Event to %s" % form.table), "/%s/%s/eventref/add" % (form.view, form.instance.handle), icon="+") # )
        retval += make_icon_button(form._("Add Existing Event to %s" % form.table), "/%s/%s/eventref/share" % (form.view, form.instance.handle), icon="p") # )
    else:
        retval += """&nbsp;""" # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    #if act == "view":
        #count = 1
        #retval = retval.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
        #retval = retval.replace("}}", """</div>""")
        #for (djevent, event_ref) in event_list:
        #    item = form.instance.__class__.__name__.lower()
        #    retval = retval.replace("[[x%d]]" % count, make_icon_button("x", "/%s/%s/remove/eventref/%d" % (item, form.instance.handle, count)))
        #    retval = retval.replace("[[^%d]]" % count, make_icon_button("^", "/%s/%s/up/eventref/%d" % (item, form.instance.handle, count)))
        #    retval = retval.replace("[[v%d]]" % count, make_icon_button("v", "/%s/%s/down/eventref/%d" % (item, form.instance.handle, count)))
        #    count += 1
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
        (form._("Note Preview"), 15),
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
                             link="/person/%s/name/%s" % (form.instance.handle, count + 1))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Name"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def surname_table(form, user, action):
    person_handle = args[0]
    order = args[1]
    retval = ""
    has_data = False
    cssid = "tab-surnames"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Order"),  10),
        (form._("Surname"), 10),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Surname"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    # if user or form.instance.public:
    #     try:
    #         name = obj.name_set.filter(order=order)[0]
    #     except:
    #         name = None
    #     if name:
    #         for surname in name.surname_set.all().order_by("order"):
    #             table.append_row(str(surname.order), surname)
    #             has_data = True
    #         retval += table.get_html(action)
    #     else:
    #         retval += "<p id='error'>No such name order = %s</p>" % order
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def citation_table(form, user, action):
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
        for citation_ref in form.instance.citation_list:
            if citation_ref:
                citation = form.database.get_citation_from_handle(citation_ref)
                table.append_row(citation.gid,
                                 citation.confidence,
                                 citation.page,
                                 link="/citation/%s" % citation.handle)
                has_data = True
                count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add New Citation"), "FIXME", icon="+")
        retval += make_icon_button(form._("Add Existing Citation"), "FIXME", icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def repository_table(form, user, action):
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
        for repo_ref in form.instance.reporef_list:
            handle = repo_ref.ref
            repo = form.database.get_repository_from_handle(handle)
            table.append_row(repo.gid,
                             repo.name,
                             repo_ref.call_number,
                             repo.type)
            has_data = True
            count += 1;
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add New Repository"), "FIXME", icon="+")
        retval += make_icon_button(form._("Add Existing Repository"), "FIXME", icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def note_table(form, user, action):
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
        notes = Struct.wrap(form.instance, form.database).note_list;
        links = []
        count = 1
        for note in notes:
            table.append_row(note.gid,
                             str(note.type.string),
                             note.text.string[:50],
                             link="/note/%s" % note.instance.handle)
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add New Note"), "FIXME", icon="+")
        retval += make_icon_button(form._("Add Existing Note"), "FIXME", icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    text = table.get_html(action)
    text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
    text = text.replace("}}", """</div>""")
    retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def data_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-data"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Type"), 39),
        (form._("Value"), 50),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        # /data/$act/citation/%s
        retval += make_icon_button(form._("Add Data"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    # if user or form.instance.public:
    #     item_class = obj.__class__.__name__.lower()
    #     if item_class == "citation":
    #         refs = models.CitationAttribute.objects.filter(citation=obj).order_by("order")
    #     elif item_class == "source":
    #         refs = models.SourceAttribute.objects.filter(source=obj).order_by("order")
    #     count = 1
    #     for ref in refs:
    #         if item_class == "citation":
    #             ref_obj = ref.citation
    #         elif item_class == "source":
    #             ref_obj = ref.source
    #         table.append_row(
    #             Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user else "",
    #             ref_obj.key,
    #             ref_obj.value,
    #             )
    #         has_data = True
    #         count += 1
        # text = table.get_html(action)
        # text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
        # text = text.replace("}}", """</div>""")
        # count = 1
        # for repo_ref in refs:
        #     text = text.replace("[[x%d]]" % count, make_icon_button("x", "/%s/%s/remove/attribute/%d" % (item_class, obj.handle, count)))
        #     text = text.replace("[[^%d]]" % count, make_icon_button("^", "/%s/%s/up/attribute/%d" % (item_class, obj.handle, count)))
        #     text = text.replace("[[v%d]]" % count, make_icon_button("v", "/%s/%s/down/attribute/%d" % (item_class, obj.handle, count)))
        #     count += 1
        # retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def attribute_table(form, user, action):
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
    if user or form.instance.public:
        for attribute in form.instance.attribute_list:
            table.append_row(attribute.type.string,
                             attribute.value,
                             link="/%s/%s/attribute/%s" %
                             (form.view, form.instance.handle, count))
            count += 1
            has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Attribute"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def address_table(form, user, action): #TODO: Make table customizable (For instance, if user desires to display counties or lat/long)
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
    s = Struct.wrap(form.instance, form.database)
    count = 1
    for address in s.address_list:
        table.append_row(address.date.text,
                         address.location.street,
                         address.location.city,
                         address.location.state,
                         address.location.country,
                         link="/%s/%s/address/%s" %
                         (form.view, form.instance.handle, count))
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Address"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def media_table(form, user, action):
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
    if user or form.instance.public:
        for media_ref in form.instance.media_list:
            media = form.database.get_media_from_handle(media_ref.ref)
            table.append_row(media.desc,
                             media.mime,
                             media.path,
                             link="/media/%s" % media.handle)
            has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add New Media"), "FIXME", icon="+")
        retval += make_icon_button(form._("Add Existing Media"), "FIXME", icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def internet_table(form, user, action):
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
    s = Struct.wrap(form.instance, form.database)
    count = 1
    for url in s.urls:
        table.append_row(url.type.string,
                         url.path,
                         url.desc,
                         link="/%s/%s/url/%s" %
                         (form.view, form.instance.handle, count))
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Internet"), "FIXME", icon="+")
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
        retval += make_icon_button(form._("Add Association"), "FIXME", icon="+")
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
                link="/%s/%s/association/%s" % (
                    form.view, form.instance.handle, count)
            )
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
    # if user or form.instance.public:
    #     # FIXME: location confusion!
    #     # The single Location on the Location Tab is here too?
    #     # I think if Parish is None, then these are single Locations;
    #     # else they are in the table of alternate locations
    #     for location in obj.location_set.all().order_by("order"):
    #         table.append_row(
    #             location.street,
    #             location.locality,
    #             location.city,
    #             location.state,
    #             location.country)
    #         has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add Address"), "FIXME", icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html(action)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def lds_table(form, user, action):
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
    s = Struct.wrap(form.instance, form.database)
    count = 1
    if user or form.instance.public:
        for lds in s.lds_ord_list:
            date = lds.date.instantiate()
            table.append_row(lds.type,
                             date_display(date) if date else "",
                             lds.status,
                             lds.temple,
                             lds.place.title,
                             link="/person/%s/lds/%s" %
                             (form.instance.handle, count))
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and action == "view":
        retval += make_icon_button(form._("Add LDS"), "FIXME", icon="+")
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
        count = 0
        for family in s.family_list:
            table1.append_row(family.gid,
                              sa.describe(family.instance), link="/family/%s" % family.instance.handle)
            has_data = True
            count += 1
        for family in s.parent_family_list:
            table2.append_row(family.gid,
                              sa.describe(family.instance), link="/family/%s" % family.instance.handle)
            has_data = True
            count += 1
        text1 = """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
        if user and action == "view":
            text1 += make_icon_button(form._("Add as Spouse to New Family"),
                                      "/family/add/spouse/%s" % form.instance.handle,
                                      icon="+")
            text1 += make_icon_button(form._("Add as Spouse to Existing Family"),
                                      "/family/share/spouse/%s" % form.instance.handle,
                                      icon="p")
        else:
            text1 += nbsp("") # to keep tabs same height
        text1 += """</div>"""
        text1 += table1.get_html(action, tab_height="100%")
        text2 = """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
        if user and action == "view":
            text2 += make_icon_button(form._("Add as Child to New Family"),
                                      "/family/add/child/%s" % form.instance.handle,
                                      icon="+")
            text2 += make_icon_button(form._("Add as Child to Existing Family"),
                                      "/family/share/child/%s" % form.instance.handle,
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
        table.append_row(obj_type, sa.describe(obj), obj.gid, link="/%s/%s" % (obj_type.lower(), handle))
        has_data = True
    retval += table.get_html(action)
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def source_citation_table(form, user, action):
    retval = ""
    has_data = False
    cssid = "tab-citations"
    table = Table(form)
    table.set_columns(
        ("", 11),
        (form._("Title"), 29),
        (form._("Author"), 20),
        (form._("Page"), 20),
        (form._("ID"), 20),
    )
    ## Loop
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
                         link="/person/%s" % handle)
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    retval += "&nbsp;"
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
