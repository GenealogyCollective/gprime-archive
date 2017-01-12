#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2015 Gramps Development Team
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

import logging
import math
import time
import json
import html
import re

from gprime.display.name import NameDisplay
from gprime.datehandler import displayer, parser
from gprime.simple import SimpleAccess
from gprime.utils.id import create_id

nd = NameDisplay().display
dd = displayer.display
dp = parser.parse

class Row(list):
    """
    """

class Column(object):
    """
    """
    def __init__(self, string, width):
        self.string = string
        self.width = width

    def __str__(self):
        return self.string

    def __len__(self):
        return len(self.string)

class Form(object):
    """
    """
    _class = None
    edit_fields = []
    select_fields = []
    env_fields = []
    order_by = []
    post_process_functions = {}
    search_terms = {}
    link = None
    where = None
    page_size = 25
    count_width = 5
    table = None

    def __init__(self, handler, instance=None):
        # scheme is a map from FIELD to Python Type, list[Gramps objects], or Handle
        self.handler = handler
        self.database = self.handler.database
        self._ = self.handler.app.get_translate_func(self.handler.current_user)
        self.instance = instance
        if self.table in self.database.get_table_names():
            self._class = self.database.get_table_func(self.table, "class_func")
            self.schema = self._class.get_schema()
        else:
            self._class = None
            self.schema = None
        self.where = None
        self.log = logging.getLogger(".Form")
        self.set_post_process_functions()
        self.sa = SimpleAccess(self.database)
        self.original_select_fields = self.select_fields

    def make_url(self, *parts):
        """
        Return the url to a primary object, if one, else view.
        """
        if parts:
            parts = [str(arg) for arg in parts]
            if parts[0].startswith("#"):
                parts = "".join(parts)
            else:
                parts = "/" + ("/".join(parts))
        else:
            parts = ""
        if self.instance:
            return "%s/%s/%s%s" % (self.handler.app.prefix, self.view, self.instance.handle, parts)
        else:
            return "%s/%s%s" % (self.handler.app.prefix, self.view, parts)

    def set_post_process_functions(self):
        pass

    def get_column_count(self):
        return len(self.select_fields) + 1

    def make_query(self, **kwargs):
        """
        Turn a dictionary into a URL query.
        """
        kwargs.update({"search": self.search})
        query = ""
        for kw in kwargs:
            if kwargs[kw]:
                if query == "":
                    query += "?"
                else:
                    query += "&"
                query += "%s=%s" % (kw, self.escape(kwargs[kw]))
        return query

    def escape(self, expr):
        """
        Escape expressions to make sure that they are URL
        usable.
        """
        ## FIXME: escape all others too
        if isinstance(expr, str):
            return expr.replace("%", "&#37;")
        else:
            return expr

    def get_table_count(self):
        return self.database.get_table_func(self.table,"count_func")()

    def get_page_controls(self, page):
        total = self.get_table_count()
        records = self.rows.total
        matching = len(self.rows)
        total_pages = math.ceil(records / self.page_size)
        return ("""<div align="center" style="background-color: lightgray; border: 1px solid black; border-radius:5px; margin: 0px 1px; padding: 1px;">""" +
                self.make_button("<<", self.make_url(self.make_query(page=1))) +
                " | " +
                self.make_button("<", "/" + self.view + (self.make_query(page=max(page - 1, 1)))) +
                (" | <b>Page</b> %s of %s | " % (page, total_pages)) +
                self.make_button(">", "/" + self.view + self.make_query(page=min(page + 1, total_pages))) +
                " | " +
                self.make_button(">>", "/" + self.view + self.make_query(page=total_pages)) +
                (" | <b>Showing</b> %s/%s <b>of</b> %s <b>in</b> %.4g seconds" % (matching, records, total, round(self.rows.time, 4))) +
                "</div>")

    def parse_where(self, search_pair):
        """
        search_pair: field OP value | search_pair OR search_pair
        """
        if "|" in search_pair:
            search_pairs = [s.strip() for s in search_pair.split("|")]
            return ["OR", [self.parse_where(pair) for pair in search_pairs]]
        elif "," in search_pair:
            search_pairs = [s.strip() for s in search_pair.split(",")]
            return ["AND", [self.parse_where(pair) for pair in search_pairs]]
        if "^" in search_pair: # second level or
            search_pairs = [s.strip() for s in search_pair.split("^")]
            return ["OR", [self.parse_where(pair) for pair in search_pairs]]
        elif "&" in search_pair:  # second level and
            search_pairs = [s.strip() for s in search_pair.split("&")]
            return ["AND", [self.parse_where(pair) for pair in search_pairs]]
        elif "!=" in search_pair:
            field, term = [s.strip() for s in search_pair.split("!=", 1)]
            if "%" in term:
                return self.expand_fields(field, "NOT LIKE", term)
            else:
                return self.expand_fields(field, "!=", term)
        elif "=" in search_pair:
            field, term = [s.strip() for s in search_pair.split("=", 1)]
            if "%" in term:
                return self.expand_fields(field, "LIKE", term)
            else:
                return self.expand_fields(field, "=", term)
        else: # search all defaults, OR
            or_where = []
            for field in self.default_search_fields:
                term = search_pair.strip()
                if "%" in term:
                    or_where.append(self.expand_fields(field, "LIKE", term))
                else:
                    or_where.append(self.expand_fields(field, "LIKE",
                                                       "%" + term + "%"))
            return ["OR", or_where]

    def expand_fields(self, field, op, term):
        """
        Return (field, op, term) or ["OR", ...]
        """
        # check for named aliases:
        field = self.search_terms.get(field, field)
        term = self.fix_term(term)
        # replace term for common values
        if isinstance(field, (list, tuple)):
            or_where = []
            for field in field:
                field = self.database.get_table_func(self.table,"class_func").get_field_alias(field)
                or_where.append((field, op, term))
            return ["OR", or_where]
        else:
            field = self.database.get_table_func(self.table,"class_func").get_field_alias(field)
            return (field, op, term)

    def fix_term(self, term):
        """
        Turn string terms into common values
        """
        term = term.strip()
        if term == "[]":
            term = []
        elif term == "None":
            term = None
        elif term.isdigit():
            term = int(term)
        elif ((term.startswith('"') and term.endswith('"')) or
              (term.startswith("'") and term.endswith("'"))):
            term = term[1:-1]
        return term

    def parse(self, search):
        """
        Returns (column_names, where)
        """
        match = re.match("SELECT (.*) WHERE (.*)", search, re.IGNORECASE)
        if match:
            return match.groups()
        else:
            match = re.match("SELECT (.*)", search, re.IGNORECASE)
            if match:
                return match.groups()[0], None
            else:
                return None, search

    def parse_select(self, search):
        """
        """
        fields = [col.strip() for col in search.split(",")]
        retval = []
        for field in fields:
            field = self.database.get_table_func(self.table,"class_func").get_field_alias(field)
            retval.append(field)
        return retval

    def select(self, page=1, search=None):
        self.page = page - 1
        self.search = search
        self.where = None
        if search:
            select_fields, where = self.parse(search)
            if select_fields:
                select_fields = self.parse_select(select_fields)
                cols = len(select_fields)
                width = 100 // cols
                self.select_fields = [(field, width) for field in select_fields]
                # Make sure these fields have something in them:
                select_where = ["OR", [(field, "!=", None) for field in select_fields]]
            else:
                self.select_fields = self.original_select_fields
                select_where = None
            if where:
                where = self.parse_where(where)
                if len(where) == 2:
                    self.where = where
                elif len(where) == 3:
                    self.where = ["AND", [where]]
                elif len(where) == 4:
                    self.where = ["AND", [where]]
                # FIXME: bug where None in select_where is different from ""
                #if select_where:
                #    self.where = ["AND", [self.where, select_where]]
            elif select_where:
                self.where = select_where
        #self.select_fields = [("tag_list.0.name", 50), ("note_list.0.gid", 50)]
        #self.where = ['OR', [('tag_list.name', '!=', None),
        #                      ("note_list.gid", "!=", None)]]
        self.log.debug("search: " + search)
        self.log.debug("where: " + str(self.where))
        self.log.debug("select: " + str(self.select_fields))
        queryset = self.database.get_queryset_by_table_name(self.table)
        queryset.limit(start=self.page * self.page_size, count=self.page_size)
        queryset.order_by = self.order_by
        queryset.where_by = self.where
        class Result(list):
            time = 0
            total = 0
        start_time = time.time()
        self.rows = Result(queryset.select(*(self.get_select_fields() + self.env_fields)))
        queryset = self.database.get_queryset_by_table_name(self.table)
        queryset.where_by = self.where
        self.rows.total = queryset.count()
        self.rows.time = time.time() - start_time
        return ""

    def get_select_fields(self):
        return [field for (field, width) in self.select_fields]

    def get_select_field(self, position):
        return [field for (field, width) in self.select_fields][position]

    def get_select_widths(self):
        return [width for (field, width) in self.select_fields]

    def get_select_width(self, position):
        return [width for (field, width) in self.select_fields][position]

    def get_rows(self, page=0):
        self.log.debug("getting page = " + str(page))
        retval = []
        count = (self.page * self.page_size) + 1
        url = """<a href="%s?page=%s" class="browsecell">%s</a>"""
        for row in self.rows:
            retval_row = Row()
            env = {}
            for field_name in self.env_fields:
                data = row[field_name]
                env[field_name] = data
            if self.link:
                link = self.link % env
                retval_row.append(Column(url % (self.handler.app.make_url(link), page, count), self.count_width))
            else:
                retval_row.append(Column(count, self.count_width))
            for field_name, field_width in self.select_fields:
                data = row[field_name]
                if field_name in self.post_process_functions:
                    data = self.post_process_functions[field_name](data, env)
                if self.link:
                    link = self.link % env
                    data = data if data else "&nbsp;"
                    data = """<a href="%s?page=%s" class="browsecell">%s</a>""" % (self.handler.app.make_url(link), page, data)
                retval_row.append(Column(data, field_width))
            retval.append(retval_row)
            count += 1
        return retval

    def get_column_labels(self):
        headings = Row()
        headings.append(Column("#", self.count_width))
        for field, width in self.select_fields:
            headings.append(Column(self._class.get_label(field, self._), width))
        return headings

    def get_label(self, field):
        return self.instance.get_label(field, self._)

    def render(self, field, user, action, js=None, _class=None, link=None, **kwargs):
        from gprime.lib.handle import HandleClass
        from gprime.lib.struct import Struct
        from gprime.lib.grampstype import GrampsType
        from gprime.lib.date import Date
        data = self.instance.get_field(field, self.database)
        field_name = field
        if action == "edit" and field not in self.edit_fields:
            self.log.warning("You are trying to edit field '%s', but it is NOT in the edit_fields list: %s" % (field, self.edit_fields))
        if isinstance(data, (list, tuple)): ## Tags or rect
            if len(data) == 4 and all([isinstance(item, int) for item in data]): # rect
                return str(data)
            s = Struct.wrap(self.instance, self.database)
            data = s.getitem_from_path(field.split("."))
            ## a list of handles
            _class = """class ="%s" """ % _class if _class else ""
            if action == "edit":
                retval = """<select multiple="multiple" name="%s" id="id_%s" style="width: 100%%; height: 100%%" %s>""" % (field_name, field, _class)
            else:
                url = self.handler.app.make_url("/tag/")
                retval = """<select multiple="multiple" name="%s" id="id_%s" style="width: 100%%; height: 100%%" onclick="location = &quot;%s&quot; + this.value;" %s>""" % (field_name, field, url, _class)
            tags = set()
            for item in data:
                ## Tags:
                name = item.name
                handle = item.instance.handle
                retval += """<option value="%s" selected>%s</option>""" % (handle, name)
                tags.add(handle)
            if action == "edit":
                for tag in self.database.Tag.select():
                    if tag.handle not in tags:
                        retval += """<option value="%s">%s</option>""" % (tag.handle, tag.name)
            retval += "</select>"
        elif isinstance(data, bool): # Booleans (private, probably alive)
            env = {
                "field": field,
                "field_name": field_name,
                "checked": "checked" if data else "",
                "disabled": "" if action == "edit" else "disabled",
                "_class": """class ="%s" """ % _class if _class else "",
            }
            return """<input type="checkbox" %(checked)s id="id_%(field)s" %(disabled)s name="%(field_name)s" %(_class)s></input>""" % env
        elif isinstance(data, Date):
            if action == "edit":
                env = {
                    "field": field,
                    "field_name": field_name,
                    "value": data.text,
                    "disabled": "" if action == "edit" else "disabled",
                    "_class": """class ="%s" """ % _class if _class else "",
                }
                return """<input type="text" id="id_%(field)s" %(disabled)s name="%(field_name)s" value="%(value)s" %(_class)s></input>""" % env
            else:
                return data.text
        elif isinstance(data, GrampsType):
            env = {
                "field": field,
                "field_name": field_name,
                "disabled": "" if action == "edit" else "disabled",
                "_class": """class ="%s" """ % _class if _class else "",
            }
            retval = """<select name="%(field_name)s" %(disabled)s id="id_%(field)s" style="width: 100%%" %(_class)s>""" % env
            if action == "edit":
                for option in data._DATAMAP:
                    env["selected"] = "selected" if option[2] == data.string else ""
                    env["value"] = option[0] # number
                    env["string"] = option[1] # translated
                    retval += """<option value="%(value)s" %(selected)s>%(string)s</option>""" % env
            else:
                env["value"] = data.value
                env["string"] = data.string
                retval += """<option value="%(value)s" selected>%(string)s</option>""" % env
            retval += "</select>"
        else: # text field
            retval = data
            if action in ["edit", "add"]:
                id = js if js else "id_" + field
                dict = {"id": id,
                        "name": field,
                        "field_name": field_name,
                        "value": retval,
                        "_class": """class ="%s" """ % _class if _class else "",
                }
                retval = """<input id="%(id)s" type="text" name="%(field_name)s" value="%(value)s" style="display:table-cell; width:100%%" %(_class)s></input>""" % dict
        if action == "view":
            ## FIXME: kwargs may have ints
            ## This is useful in views; not sure about detail view
            if field in self.post_process_functions:
                retval = self.post_process_functions[field](data, {})
        if link:
            for key in kwargs:
                kwargs[key] = str(kwargs[key])
            retval = '''<a href="''' +  (self.handler.app.make_url(link % kwargs)) + '''">''' + retval + """</a>"""
        return str(retval)

    def get(self, field):
        return self.instance.get_field(field, self.database)

    def get_json(self):
        return html.escape(json.dumps(self.instance.to_struct()))

    def load_data(self):
        from gprime.lib.grampstype import GrampsType
        from gprime.lib.date import Date
        # go thorough fields and save values
        for field in self.edit_fields:
            try:
                part = self.instance.get_field(field)
            except:
                self.log.warning("field '%s' not found in object; valid fields: %s", field, self.instance.to_struct().keys())
                continue
            if isinstance(part, (list, tuple)): # Tag
                try:
                    value = self.handler.get_arguments(field)
                except:
                    self.log.warning("field '%s' not found in form; valid fields: %s", field, self.edit_fields)
                    value = None
                part[:] = value
            elif isinstance(part, bool): # Bool
                try:
                    value = self.handler.get_argument(field)
                except:
                    value = "off"
                self.instance.set_field(field, True if value == "on" else False)
            elif isinstance(part, GrampsType): # type
                # FIXME: lookup type number, set item to Type()
                self.log.warning("save grampstype: %s", field)
                pass
            elif isinstance(part, Date):
                # FIXME: parse, save date
                self.log.warning("save date: %s", field)
                pass
            else:
                try:
                    value = self.handler.get_argument(field)
                except:
                    self.log.warning("field '%s' not found in form; valid fields: %s", field, self.edit_fields)
                    value = None
                    continue
                self.instance.set_field(field, value)

    def save(self):
        self.load_data()
        transaction = self.database.get_transaction_class()
        commit = self.database.get_table_func(self._class.__name__,"commit_func")
        if not self.instance.handle:
            self.instance.handle = create_id()
        ## FIXME: should gid be assigned before this? YES, I think, and checked to make
        ## sure no dups
        with transaction("Gramps Connect", self.database) as trans:
            commit(self.instance, trans)

    def get_person_from_handle(self, handle, env):
        if handle:
            person = self.database.get_person_from_handle(handle)
            if person:
                return nd(person)
        return ""

    def display_name_from_field_handle(self, field):
        handle = self.instance.get_field(field, self.database)
        person = self.database.get_person_from_handle(handle)
        if person:
            return nd(person)
        else:
            return ""

    def display_event_from_field_handle(self, field):
        handle = self.instance.get_field(field, self.database)
        event = self.database.get_event_from_handle(handle)
        if event:
            return self.sa.describe(event)
        else:
            return ""

    def display_media_from_field_handle(self, field):
        handle = self.instance.get_field(field, self.database)
        obj = self.database.get_media_from_handle(handle)
        if obj:
            return self.sa.describe(obj)
        else:
            return ""

    def display_place_from_field_handle(self, field):
        handle = self.instance.get_field(field, self.database)
        obj = self.database.get_place_from_handle(handle)
        if obj:
            return self.sa.describe(obj)
        else:
            return ""

    def display_repository_from_field_handle(self, field):
        handle = self.instance.get_field(field, self.database)
        obj = self.database.get_repository_from_handle(handle)
        if obj:
            return self.sa.describe(obj)
        else:
            return ""

    def display_name(self, person):
        return nd(person)

    def get_media(self, width, height=None):
        if hasattr(self.instance, "media_list"):
            if self.instance.media_list:
                media_ref = self.instance.media_list[0]
                media_handle = media_ref.ref
                if media_ref.rect:
                    x1, y1, x2, y2 = media_ref.rect
                    w = x2 - x1
                    h = y2 - y1
                    env = {
                        "handle": media_handle,
                        "width": width,
                        "x": x1, "y": y1, "w": w, "h": h,
                    }
                    full = self.handler.app.make_url("/imageserver/%(handle)s/pct:%(x)s,%(y)s,%(w)s,%(h)s/full/0/default.jpg" % env)
                    rect = self.handler.app.make_url("/imageserver/%(handle)s/pct:%(x)s,%(y)s,%(w)s,%(h)s/%(width)s,/0/default.jpg" % env)
                    return (
                        """<a href="%(full)s"/>""" +
                        """<img src="%(rect)s"/>""" +
                        """</a>"""
                    ) % {"full": full, "rect": rect}
                else:
                    env = {
                            "handle": media_handle,
                            "width": width,
                        }
                    full = self.handler.app.make_url("/imageserver/%(handle)s/full/full/0/default.jpg" % env)
                    rect = self.handler.app.make_url("/imageserver/%(handle)s/full/%(width)s,/0/default.jpg" % env)
                    return (
                        """<a href="%(full)s">""" +
                        """<img src="%(rect)s"/></a>""") % {"full": full, "rect": rect}
        else:
            env = {
                    "handle": self.instance.handle,
                    "width": width,
                }
            full = self.handler.app.make_url("/imageserver/%(handle)s/full/full/0/default.jpg" % env)
            rect = self.handler.app.make_url("/imageserver/%(handle)s/full/%(width)s,/0/default.jpg" % env)
            return (
                """<a href="%(full)s">""" +
                """<img src="%(rect)s"/></a>""") % {"full": full, "rect": rect}
        return ""

    def set_post_process_functions(self):
        """
        Set the post_process_functions dictionary.
        """
        self.post_process_functions = {
            "date": self.render_date,
            "change": self.render_change,
            "gender": self.render_gender,
            "birth_ref_index": self.event_index,
            "death_ref_index": self.event_index,
            "text.string": self.preview,
            #"tag_list": self.get_tag_from_handle:name
        }

    def preview(self, text, env):
        return text[:100]

    def birth_date(self, person):
        return self.sa.birth_date(person)

    def death_date(self, person):
        return self.sa.death_date(person)

    def family_father(self, family):
        return self.sa.father(family)

    def family_mother(self, family):
        return self.sa.mother(family)

    def render_date(self, date, env):
        return dd(date)

    def render_change(self, change, env):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(change))

    def event_index(self, index, env):
        """
        Used for revent_ref_index lookups.
        """
        if 0 <= index < len(env["event_ref_list"]):
            event_ref = env["event_ref_list"][index]
            if event_ref.ref:
                event = self.database.get_event_from_handle(event_ref.ref)
                if event:
                    return event.date
        return ""

    def render_gender(self, gender_code, env):
        """
        Text for gender codes.
        """
        return [self._("Female"), self._("Male"), self._("Unknown")][gender_code]

    def describe(self):
        """
        Textual description of this instance.
        """
        return self.sa.describe(self.instance)

    def make_button(self, text, link):
        return """<input type="button" value="%s" onclick="location.href='%s';"></input>""" % (
            text,
            self.handler.app.make_url(link))

    def make_icon_button(self, text, link, **kwargs):
        if "icon" in kwargs:
            if kwargs["icon"] == "+":
                img_src = self.handler.app.make_url("/images/add.png")
            elif kwargs["icon"] == "?":
                img_src = self.handler.app.make_url("/images/text-editor.png")
            elif kwargs["icon"] == "-":
                img_src = self.handler.app.make_url("/images/gtk-remove.png")
            elif kwargs["icon"] == "p": # pick
                img_src = self.handler.app.make_url("/images/stock_index_24.png")
            else:
                raise Exception("invalid icon: %s" % kwargs["icon"])
            return ("""<img height="22" width="22" alt="%(text)s" title="%(text)s"
     src="%(img_src)s" onmouseover="buttonOver(this)" onmouseout="buttonOut(this)"
        onclick="document.location.href='%(link)s'"
     style="background-color: lightgray; border: 1px solid lightgray; border-radius:5px; margin: 0px 1px; padding: 1px;" />
""") % {"link": self.handler.app.make_url(link % kwargs), "img_src": img_src, "text": text}
        else:
            return """<a href="%(link)s" class="browsecell">%(text)s</a>""" % {"link": self.handler.app.make_url(link % kwargs),
                                                                               "text": text}

    def make_link(self, url, text, **kwargs):
        return """<a href="%s"><b>%s</b></a>""" % ((self.handler.app.make_url(url) % kwargs), text)

    def set_class_from_url(self, url, handler):
        _ = handler.app.get_translate_func(handler.current_user)
        self.view = url.split("/")[1]
        self.table = self.view.title()
        self.tview = _(self.table)
        self._class = handler.database.get_table_func(self.table, "class_func")

    def delete(self):
        raise Exception("Need to override this in form")
