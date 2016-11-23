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
from gprime.plugins.lib.libhtml import Html
from gprime.lib import *
from gprime.lib.struct import Struct
from gprime.display.name import NameDisplay

# Globals and functions:
TAB_HEIGHT = 200
nd = NameDisplay().display

def make_button(text, link):
    return """<input type="button" value="%s" onclick="location.href='%s';" />""" % (text, link)

def make_icon_button(text, link, **kwargs):
    if "icon" in kwargs:
        if kwargs["icon"] == "+":
            img_src = "/misc/add.png"
        elif kwargs["icon"] == "?":
            img_src = "/misc/text-editor.png"
        elif kwargs["icon"] == "-":
            img_src = "/misc/gtk-remove.png"
        elif kwargs["icon"] == "p": # pick
            img_src = "/misc/stock_index_24.png"
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
    >>> table = Table("css_id")
    >>> table.set_columns(("Col1", 10), ("Col2", 90))
    >>> table.append_row("1", "2", "3")
    >>> table.append_row("4", "5", "6")
    >>> table.get_html()
    """
    def __init__(self, form, id, style=None):
        self.id = id # css id
        self.form = form
        self.column_widths = None
        self.columns = []
        self.rows = []

    def set_columns(self, *args):
        self.columns = args

    def append_row(self, *args):
        self.rows.append(list(map(nbsp, args)))

    def get_html(self, style=None, tab_height=200):
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
            cell += name
            rowhtml += cell
        table += rowhtml
        for row in self.rows:
            rowhtml = Html("tr")
            cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[0][1]), colspan="1")
            div = Html("div", style="background-color: lightgray; padding: 2px 0px 0px 2px")
            div += Html("img", height="22", width="22",
                        alt="Delete row", title="Delete row",
                        src="/misc/gtk-remove.png",
                        onmouseover="buttonOver(this)", onmouseout="buttonOut(this)",
                        onclick="document.location.href='/person/b2cfa6ca1e174b1f63d/remove/eventref/1'",
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            div += Html("img", height="22", width="22",
                        alt="Move row up", title="Move row up",
                        src="/misc/up.png",
                        onmouseover="buttonOver(this)", onmouseout="buttonOut(this)",
                        onclick="document.location.href='/person/b2cfa6ca1e174b1f63d/up/eventref/1'",
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            div += Html("img", height="22", width="22",
                        alt="Move row down", title="Move row down",
                        src="/misc/down.png",
                        onmouseover="buttonOver(this)", onmouseout="buttonOut(this)",
                        onclick="document.location.href='/person/b2cfa6ca1e174b1f63d/down/eventref/1'",
                        style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;")
            cell += div
            rowhtml += cell
            for count in range(1, len(self.columns)):
                cell = Html("td", class_="TableDataCell", width=("%s%%" % self.columns[count][1]), colspan="1")
                cell += row[count - 1]
                rowhtml += cell
            table += rowhtml
        html += table
        return str(html) #.replace("&amp;nbsp;", "&nbsp;")

def event_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-events"
    table = Table(form, "tab_table")
    event = Event()
    eventref = EventRef()
    table.set_columns(
        ("", 11),
        (event.get_label("description", form._), 19),
        (event.get_label("type", form._), 10),
        (event.get_label("gramps_id", form._),11),
        (event.get_label("date", form._), 20),
        (event.get_label("place", form._), 19),
        (eventref.get_label("role", form._), 10),
    )
    s = Struct.wrap(form.instance, form.database)
    count = 0
    for event_ref in s.event_ref_list: # eventrefs
        table.append_row(event_ref.ref.description,
                         event_ref.ref.type.string,
                         event_ref.ref.gramps_id,
                         event_ref.ref.date.from_struct(),
                         event_ref.ref.place.name.value,
                         event_ref.role.string)
        has_data = True
        count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px"/>"""
    if action == "view":
        retval += make_icon_button(form._("Add New Event"), (link % kwargs).replace("$act", "add"), icon="+") # )
        retval += make_icon_button(form._("Add Existing Event"), (link % kwargs).replace("$act", "share"), icon="p") # )
    else:
        retval += """&nbsp;""" # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
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

def name_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-names"
    table = Table(form, "tab_table")
    table.set_columns(
        ("", 11),
        (form._("Name"), 29),
        (form._("Type"), 20),
        (form._("Group As"), 15),
        (form._("Source"), 10),
        (form._("Note Preview"), 15),
    )
    if user or form.instance.public:
        #         links.append(('URL',
        #                       # url is "/person/%s/name"
        #                       (url % name.person.handle) + ("/%s" % name.order)))
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
                             str(name.type) + ["", " (preferred)"][int(count == 0)],
                             name.group_as,
                             ["No", "Yes"][citationq],
                             note_text)
            has_data = True
            count += 1
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Name"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def surname_table(form, user, action, link=None, **kwargs):
    person_handle = args[0]
    order = args[1]
    retval = ""
    has_data = False
    cssid = "tab-surnames"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Order"),  10),
        (form._("Surname"), 10),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Surname"), (link % kwargs), icon="+")
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
    #         retval += table.get_html()
    #     else:
    #         retval += "<p id='error'>No such name order = %s</p>" % order
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def citation_table(form, user, action, link=None, **kwargs):
    # FIXME: how can citation_table and source_table both be on same
    # page? This causes problems with form names, tab names, etc.
    retval = ""
    has_data = False
    cssid = "tab-sources"
    table = Table(form, "tab_table")
    table.set_columns(
        ("", 11),
        (form._("ID"), 10),
        (form._("Confidence"), 49),
        (form._("Page"), 30),
    )
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     citation_refs = db.dji.CitationRef.filter(object_type=obj_type,
    #                                            object_id=obj.id).order_by("order")
    #     links = []
    #     count = 1
    #     for citation_ref in citation_refs:
    #         if citation_ref.citation:
    #             citation = table.db.get_citation_from_handle(
    #                 citation_ref.citation.handle)
    #             table.append_row(Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user and link and action == "view" else "",
    #                       citation.gramps_id,
    #                       str(citation.confidence),
    #                       str(citation.page),
    #                       )
    #             links.append(('URL', citation_ref.get_url()))
    #             has_data = True
    #             count += 1
    #     table.links(links)
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add New Citation"), (link % kwargs).replace("$act", "add"), icon="+")
        retval += make_icon_button(form._("Add Existing Citation"), (link % kwargs).replace("$act", "share"), icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    # if user and link and action == "view":
    #     retval = retval.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
    #     retval = retval.replace("}}", """</div>""")
    #     count = 1
    #     for citation_ref in citation_refs:
    #         item = obj.__class__.__name__.lower()
    #         retval = retval.replace("[[x%d]]" % count, make_icon_button("x", "/%s/%s/remove/citationref/%d" % (item, obj.handle, count), icon="x"))
    #         retval = retval.replace("[[^%d]]" % count, make_icon_button("^", "/%s/%s/up/citationref/%d" % (item, obj.handle, count)), icon="^")
    #         retval = retval.replace("[[v%d]]" % count, make_icon_button("v", "/%s/%s/down/citationref/%d" % (item, obj.handle, count), icon="v"))
    #         count += 1
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def repository_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-repositories"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("ID"), 11),
        (form._("Title"), 49),
        (form._("Call number"), 20),
        (form._("Type"), 20),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add New Repository"), (link % kwargs).replace("$act", "add"), icon="+")
        retval += make_icon_button(form._("Add Existing Repository"), (link % kwargs).replace("$act", "share"), icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     refs = db.dji.RepositoryRef.filter(object_type=obj_type,
    #                                     object_id=obj.id)
    #     count = 1
    #     for repo_ref in refs:
    #         repository = repo_ref.ref_object
    #         table.append_row(
    #             Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user else "",
    #             repository.gramps_id,
    #             repository.name,
    #             repo_ref.call_number,
    #             str(repository.repository_type),
    #             )
    #         has_data = True
    #         count += 1
    #     text = table.get_html()
    #     text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
    #     text = text.replace("}}", """</div>""")
    #     count = 1
    #     for repo_ref in refs:
    #         item = obj.__class__.__name__.lower()
    #         text = text.replace("[[x%d]]" % count, make_icon_button("x", "/%s/%s/remove/repositoryref/%d" % (item, obj.handle, count)))
    #         text = text.replace("[[^%d]]" % count, make_icon_button("^", "/%s/%s/up/repositoryref/%d" % (item, obj.handle, count)))
    #         text = text.replace("[[v%d]]" % count, make_icon_button("v", "/%s/%s/down/repositoryref/%d" % (item, obj.handle, count)))
    #         count += 1
    #     retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def note_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-notes"
    table = Table(form, "tab_table")
    table.set_columns(
        ("", 11),
        (form._("ID"), 10),
        (form._("Type"), 20),
        (form._("Note"), 59),
    )
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     note_refs = db.dji.NoteRef.filter(object_type=obj_type,
    #                                    object_id=obj.id).order_by("order")
    #     links = []
    #     count = 1
    #     for note_ref in note_refs:
    #         note = note_ref.ref_object
    #         table.append_row(Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user else "",
    #                   note.gramps_id,
    #                   str(note.note_type),
    #                   note.text[:50]
    #                   )
    #         links.append(('URL', note_ref.get_url()))
    #         has_data = True
    #         count += 1
    #     table.links(links)
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add New Note"), (link % kwargs).replace("$act", "add"), icon="+")
        retval += make_icon_button(form._("Add Existing Note"), (link % kwargs).replace("$act", "share"), icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    text = table.get_html()
    text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
    text = text.replace("}}", """</div>""")
    # if user or form.instance.public:
    #     count = 1
    #     for note_ref in note_refs:
    #         item = obj.__class__.__name__.lower()
    #         text = text.replace("[[x%d]]" % count, make_icon_button("x", "/%s/%s/remove/noteref/%d" % (item, obj.handle, count)))
    #         text = text.replace("[[^%d]]" % count, make_icon_button("^", "/%s/%s/up/noteref/%d" % (item, obj.handle, count)))
    #         text = text.replace("[[v%d]]" % count, make_icon_button("v", "/%s/%s/down/noteref/%d" % (item, obj.handle, count)))
    #         count += 1
    retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def data_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-data"
    table = Table(form, "tab_table")
    table.set_columns(
        ("", 11),
        (form._("Type"), 39),
        (form._("Value"), 50),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        # /data/$act/citation/%s
        retval += make_icon_button(form._("Add Data"), (url.replace("$act", "add") % kwargs), icon="+")
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
        # text = table.get_html()
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

def attribute_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-attributes"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Value"), 10),
    )
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     attributes = db.dji.Attribute.filter(object_type=obj_type,
    #                                       object_id=obj.id)
    #     for attribute in attributes:
    #         table.append_row(attribute.attribute_type.name,
    #                   attribute.value)
    #         has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Attribute"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def address_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-addresses"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Date"), 10),
        (form._("Address"), 10),
        (form._("City"), 10),
        (form._("State"), 10),
        (form._("Country"), 10),
    )
    # if user or form.instance.public:
    #     for address in obj.address_set.all().order_by("order"):
    #         locations = address.location_set.all().order_by("order")
    #         for location in locations:
    #             table.append_row(display_date(address),
    #                       location.street,
    #                       location.city,
    #                       location.state,
    #                       location.country)
    #             has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Address"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def media_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-media"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Description"), 10),
        (form._("Type"), 10),
        (form._("Path/Filename"), 10),
    )
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     media_refs = db.dji.MediaRef.filter(object_type=obj_type,
    #                                     object_id=obj.id)
    #     for media_ref in media_refs:
    #         media = table.db.get_media_from_handle(
    #             media_ref.ref_object.handle)
    #         table.append_row(table.db.get_media_from_handle(media.handle),
    #                   str(media_ref.ref_object.desc),
    #                   media_ref.ref_object.path)
    #         has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add New Media"), (link % kwargs).replace("$act", "add"), icon="+")
        retval += make_icon_button(form._("Add Existing Media"), (link % kwargs).replace("$act", "share"), icon="p")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def internet_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-internet"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Path"), 10),
        (form._("Description"), 10),
    )
    # if user or form.instance.public:
    #     urls = db.dji.Url.filter(person=obj)
    #     for url_obj in urls:
    #         table.append_row(str(url_obj.url_type),
    #                   url_obj.path,
    #                   url_obj.desc)
    #         has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Internet"), (str(url) % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def association_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-associations"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Name"), 10),
        (form._("ID"), 10),
        (form._("Association"), 10),
    )
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Association"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    if user or form.instance.public:
    #         links = []
    #         count = 1
    #         associations = person.get_person_ref_list()
    #         for association in associations: # PersonRef
    #             table.append_row(Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user and link and action == "view" else "",
    #                       association.ref_object.get_primary_name(),
    #                       association.ref_object.gramps_id,
    #                       association.description,
    #                       )
    #             links.append(('URL', "/person/%s/association/%d" % (obj.handle, count)))
    #             has_data = True
    #             count += 1
    #         table.links(links)
        text = table.get_html()
        text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
        text = text.replace("}}", """</div>""")
    #         count = 1
    #         for association in associations: # PersonRef
    #             text = text.replace("[[x%d]]" % count, make_icon_button("x", "/person/%s/remove/association/%d" % (obj.handle, count)))
    #             text = text.replace("[[^%d]]" % count, make_icon_button("^", "/person/%s/up/association/%d" % (obj.handle, count)))
    #             text = text.replace("[[v%d]]" % count, make_icon_button("v", "/person/%s/down/association/%d" % (obj.handle, count)))
        retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def location_table(form, user, action, link=None, **kwargs):
    # obj is Place or Address
    retval = ""
    has_data = False
    cssid = "tab-alternatelocations"
    table = Table(form, "tab_table")
    table.set_columns(
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
    if user and link and action == "view":
        retval += make_icon_button(form._("Add Address"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def lds_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-lds"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Date"), 10),
        (form._("Status"), 10),
        (form._("Temple"), 10),
        (form._("Place"), 10),
    )
    # if user or form.instance.public:
    #     obj_type = ContentType.objects.get_for_model(obj)
    #     ldss = obj.lds_set.all().order_by("order")
    #     for lds in ldss:
    #         table.append_row(str(lds.lds_type),
    #                   display_date(lds),
    #                   str(lds.status),
    #                   lds.temple,
    #                   get_title(lds.place))
    #         has_data = True
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    if user and link and action == "view":
        retval += make_icon_button(form._("Add LDS"), (link % kwargs), icon="+")
    else:
        retval += nbsp("") # to keep tabs same height
    retval += """</div>"""
    retval += table.get_html()
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def person_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    text1 = ""
    text2 = ""
    table1 = Table(form, "tab_table", style="background-color: #f4f0ec;")
    table1.set_columns(
        ("As Spouse", 11),
        (form._("ID"), 10),
        (form._("Reference"), 79),
    )
    table2 = Table(form, "tab_table", style="background-color: #f4f0ec;")
    table2.set_columns(
        ("As Child", 11),
        (form._("ID"), 10),
        (form._("Reference"), 79),
    )
    if (user or form.instance.public) and action != "add":
    #     count = 1
    #     for through in models.MyFamilies.objects.filter(person=obj).order_by("order"):
    #         reference = through.family
    #         table1.row(
    #             Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user else "",
    #             reference.gramps_id,
    #             reference,
    #             )
    #         has_data = True
    #         count += 1
        text1 += table1.get_html()
        text1 = text1.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
        text1 = text1.replace("}}", """</div>""")
    #     count = 1
    #     for through in models.MyFamilies.objects.filter(person=obj).order_by("order"):
    #         reference = through.family
    #         text1 = text1.replace("[[x%d]]" % count, make_icon_button("x", "/person/%s/remove/family/%d" % (obj.handle, count)))
    #         text1 = text1.replace("[[^%d]]" % count, make_icon_button("^", "/person/%s/up/family/%d" % (obj.handle, count)))
    #         text1 = text1.replace("[[v%d]]" % count, make_icon_button("v", "/person/%s/down/family/%d" % (obj.handle, count)))
    #         count += 1
    #     # Parent Families
    #     count = 1
    #     for through in models.MyParentFamilies.objects.filter(person=obj).order_by("order"):
    #         reference = through.family
    #         table2.row(
    #             Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user else "",
    #             reference.gramps_id,
    #             reference,
    #             )
    #         has_data = True
    #         count += 1
        text2 += table2.get_html()
        text2 = text2.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
        text2 = text2.replace("}}", """</div>""")
        # count = 1
        # for through in models.MyParentFamilies.objects.filter(person=obj).order_by("order"):
        #     reference = through.family
        #     text2 = text2.replace("[[x%d]]" % count, make_icon_button("x", "/person/%s/remove/parentfamily/%d" % (obj.handle, count)))
        #     text2 = text2.replace("[[^%d]]" % count, make_icon_button("^", "/person/%s/up/parentfamily/%d" % (obj.handle, count)))
        #     text2 = text2.replace("[[v%d]]" % count, make_icon_button("v", "/person/%s/down/parentfamily/%d" % (obj.handle, count)))
        #     count += 1

    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    # retval += make_image_button2("add spouse to new family",
    #                              form._("Add as Spouse to New Family"),
    #                              "/family/add/spouse/%s" % obj.handle)
    # retval += make_image_button2("add spouse to existing family",
    #                              form._("Add as Spouse to Existing Family"),
    #                              "/family/share/spouse/%s" % obj.handle)
    # retval += "&nbsp;"
    # retval += make_image_button2("add child to new family",
    #                              form._("Add as Child to New Family"),
    #                              "/family/add/child/%s" % obj.handle)
    # retval += make_image_button2("add child to existing family",
    #                              form._("Add as Child to Existing Family"),
    #                              "/family/share/child/%s" % obj.handle)
    retval += "&nbsp;"
    retval += """</div>"""
    retval += """<div style="overflow: auto; height:%spx;">""" % TAB_HEIGHT
    retval += text1 + text2 + "</div>"
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def note_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user  or form.instance.public) and action != "add":
    #     for reference in models.NoteRef.objects.filter(ref_object=obj):
    #         ref_from_class = reference.object_type.model_class()
    #         item = ref_from_class.objects.get(id=reference.object_id)
    #         table.append_row(
    #             item.__class__.__name__,
    #             item,
    #             item.gramps_id)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def event_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     for reference in models.EventRef.objects.filter(ref_object=obj):
    #         ref_from_class = reference.object_type.model_class()
    #         try:
    #             item = ref_from_class.objects.get(id=reference.object_id)
    #         except:
    #             print("Warning: Corrupt reference: %s" % reference)
    #             continue
    #         table.append_row(
    #             item.__class__.__name__,
    #             item,
    #             item.gramps_id)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def repository_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     for reference in models.RepositoryRef.objects.filter(ref_object=obj):
    #         ref_from_class = reference.object_type.model_class()
    #         item = ref_from_class.objects.get(id=reference.object_id)
    #         table.append_row(
    #             item.__class__.__name__,
    #             item,
    #             item.gramps_id)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def citation_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        #        form._("ID")
        )
    # if (user or form.instance.public) and action != "add":
    #     for reference in models.CitationRef.objects.filter(citation=obj):
    #         ref_from_class = reference.object_type.model_class()
    #         item = ref_from_class.objects.get(id=reference.object_id)
    #         table.append_row(
    #             item.__class__.__name__,
    #             item)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def source_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     for item in obj.citation_set.all():
    #         table.append_row(
    #             item.__class__.__name__,
    #             item,
    #             item.gramps_id)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def media_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     for reference in models.MediaRef.objects.filter(ref_object=obj):
    #         ref_from_class = reference.object_type.model_class()
    #         item = ref_from_class.objects.get(id=reference.object_id)
    #         table.append_row(
    #             item.__class__.__name__,
    #             item,
    #             item.gramps_id)
    #         has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def place_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     # location, url, event, lds
    #     querysets = [obj.location_set, obj.url_set, obj.event_set, obj.lds_set]
    #     for queryset in querysets:
    #         for item in queryset.all():
    #             table.append_row(
    #                 item.__class__.__name__,
    #                 item)
    #             has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def tag_reference_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table(form, "tab_table")
    table.set_columns(
        (form._("Type"), 10),
        (form._("Reference"), 10),
        (form._("ID"), 10),
    )
    # if (user or form.instance.public) and action != "add":
    #     querysets = [obj.person_set, obj.family_set, obj.note_set, obj.media_set]
    #     for queryset in querysets:
    #         for item in queryset.all():
    #             table.append_row(
    #                 item.__class__.__name__,
    #                 item,
    #                 item.gramps_id)
    #             has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def children_table(form, user, action, link=None, **kwargs):
    retval = ""
    has_data = False
    cssid = "tab-children"
    table = Table(form, "tab_table")
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

    # family = obj
    # obj_type = ContentType.objects.get_for_model(family)
    # childrefs = db.dji.ChildRef.filter(object_id=family.id,
    #                                 object_type=obj_type).order_by("order")
    # links = []
    # count = 1
    # for childref in childrefs:
    #     child = childref.ref_object
    #     if user.is_authenticated() or obj.public:
    #         table.row(Link("{{[[x%d]][[^%d]][[v%d]]}}" % (count, count, count)) if user.is_superuser and url and act == "view" else "",
    #                   str(count),
    #                   "[%s]" % child.gramps_id,
    #                   render_name(child, user),
    #                   child.gender_type,
    #                   childref.father_rel_type,
    #                   childref.mother_rel_type,
    #                   date_as_text(child.birth, user) if child.birth else "",
    #                   )
    #         has_data = True
    #         links.append(('URL', childref.get_url()))
    #         count += 1
    #     else:
    #         table.row("",
    #                   str(count),
    #                   "[%s]" % child.gramps_id,
    #                   render_name(child, user) if not child.private else "[Private]",
    #                   child.gender_type if not child.private else "[Private]",
    #                   "[Private]",
    #                   "[Private]",
    #                   "[Private]",
    #                   )
    #         if not child.private and not childref.private:
    #             links.append(('URL', childref.get_url()))
    #         else:
    #             links.append((None, None))
    #         has_data = True
    #         count += 1
    # table.links(links)
    retval += """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">"""
    retval += "&nbsp;"
    retval += "</div>"
    text = table.get_html()

    # if user.is_superuser and url and act == "view":
    #     text = text.replace("{{", """<div style="background-color: lightgray; padding: 2px 0px 0px 2px">""")
    #     text = text.replace("}}", """</div>""")
    #     count = 1
    #     for childref in childrefs:
    #         text = text.replace("[[x%d]]" % count, make_button("x", "/family/%s/remove/child/%d" % (family.handle, count)))
    #         text = text.replace("[[^%d]]" % count, make_button("^", "/family/%s/up/child/%d" % (family.handle, count)))
    #         text = text.replace("[[v%d]]" % count, make_button("v", "/family/%s/down/child/%d" % (family.handle, count)))
    #         count += 1
    #     retval += make_button(_("Add New Person as Child"), (url.replace("$act", "add") % args))
    #     retval += make_button(_("Add Existing Person as Child"), (url.replace("$act", "share") % args))
    # else:
    #     retval += nbsp("") # to keep tabs same height
    retval += text
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def render_name(name):
    """
    Given a Gramps object, render the name and return.  This
    function uses authentication, privacy and probably_alive settings.
    """
    if name is None:
        return "[None]"
    elif isinstance(name, Person): # name is a Person
        try:
            name = person.get_primary_name()
        except:
            name = None
    elif isinstance(name, Name): # name is a Person
        pass # it is a name
    else: # no name object
        return "[No preferred name]"
    if name is None:
        return "[No preferred name]"
    if len(name.surname_list) > 0:
        surname = name.surname_list[0].surname
    else:
        surname = "[No primary surname]"
    return "%s, %s" % (surname, name.first_name)
