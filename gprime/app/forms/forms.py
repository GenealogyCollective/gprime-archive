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

import logging
import math
import time

from ..template_functions import make_button

from gprime.display.name import NameDisplay
from gprime.datehandler import displayer, parser

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

    def __init__(self, database, _, instance=None, table=None):
        # scheme is a map from FIELD to Python Type, list[Gramps objects], or Handle
        if table:
            self._class = database.get_table_func(table,"class_func")
        if self._class:
            self.schema = self._class.get_schema()
        self.table = table
        self.where = None
        self.database = database
        self.instance = instance
        self._ = _
        self.log = logging.getLogger(".Form")
        self.set_post_process_functions()

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
                make_button("<<", self.make_query(page=1)) +
                " | " +
                make_button("<", self.make_query(page=max(page - 1, 1))) +
                (" | <b>Page</b> %s of %s | " % (page, total_pages)) +
                make_button(">", self.make_query(page=min(page + 1, total_pages))) +
                " | " +
                make_button(">>", self.make_query(page=total_pages)) +
                (" | <b>Showing</b> %s/%s <b>of</b> %s <b>in</b> %.4g seconds" % (matching, records, total, round(self.rows.time, 4))) +
                "</div>")

    def parse(self, search_pair):
        """
        search_pair: field OP value | search_pair OR search_pair
        """
        if "|" in search_pair:
            search_pairs = [s.strip() for s in search_pair.split("|")]
            return ["OR", [self.parse(pair) for pair in search_pairs]]
        elif "," in search_pair:
            search_pairs = [s.strip() for s in search_pair.split(",")]
            return ["AND", [self.parse(pair) for pair in search_pairs]]
        if "^" in search_pair: # second level or
            search_pairs = [s.strip() for s in search_pair.split("^")]
            return ["OR", [self.parse(pair) for pair in search_pairs]]
        elif "&" in search_pair:  # second level and
            search_pairs = [s.strip() for s in search_pair.split("&")]
            return ["AND", [self.parse(pair) for pair in search_pairs]]
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

    def select(self, page=1, search=None):
        self.page = page - 1
        self.search = search
        self.where = None
        if search:
            where = self.parse(search)
            if len(where) == 2:
                self.where = where
            elif len(where) == 3:
                self.where = ["AND", [where]]
        self.log.debug("search: " + search)
        self.log.debug("where: " + str(self.where))
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
                retval_row.append(Column(url % (link, page, count), self.count_width))
            else:
                retval_row.append(Column(count, self.count_width))
            for field_name, field_width in self.select_fields:
                data = row[field_name]
                if field_name in self.post_process_functions:
                    data = self.post_process_functions[field_name](data, env)
                if self.link:
                    link = self.link % env
                    data = data if data else "&nbsp;"
                    data = """<a href="%s?page=%s" class="browsecell">%s</a>""" % (link, page, data)
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

    def render(self, field, user, action, js=None, link=None, **kwargs):
        data = self.instance.get_field(field, self.database)
        if isinstance(data, (list, tuple)):
            if action == "view":
                retval = ""
                for item in data:
                    if retval:
                        retval += ", "
                    retval += item
            else:
                ## a list of handles
                retval = """<select multiple="multiple" name="%s" id="id_%s" style="width: 100%%">""" % (field, field)
                count = 1
                for item in data:
                    retval += """<option value="%d" selected="selected">%s</option>""" % (count, item)
                    count += 1
                retval += "</select>"
        else:
            retval = data
            if action in ["edit", "add"]:
                id = js if js else "id_" + field
                dict = {"id": id, "name": field, "value": retval}
                retval = """<input id="%(id)s" type="text" name="%(name)s" value="%(value)s" style="display:table-cell; width:100%%">""" % dict
        if field in self.post_process_functions:
            retval = self.post_process_functions[field](data, {})
        if link and action == "view":
            retval = '''<a href="''' +  (link % kwargs) + '''">''' + retval + """</a>"""
        return str(retval)

    def get(self, field):
        return self.instance.get_field(field, self.database)

    def save(self, handler):
        # go thorough fields and save values
        for field in self.edit_fields:
            try:
                value = handler.get_argument(field)
            except:
                self.log.warning("field '%s' not found in form" % field)
                continue
            self.instance.set_field(field, value)
        transaction = self.database.get_transaction_class()
        commit = self.database.get_table_func(self._class.__name__,"commit_func")
        with transaction("Gramps Connect", self.database) as trans:
            commit(self.instance, trans)

    def get_person_from_handle(self, handle, env):
        if handle:
            person = self.database.get_person_from_handle(handle)
            if person:
                return nd(person)
        return ""

    def get_media(self, width, height=None):
        if self.instance.media_list:
            media_ref = self.instance.media_list[0]
            media_handle = media_ref.ref
            if media_ref.rect:
                x1, y1, x2, y2 = media_ref.rect
                w = x2 - x1
                h = y2 - y1
                return (
                    """<a href="/imageserver/%(handle)s/pct:%(x)s,%(y)s,%(w)s,%(h)s/full/0/default.jpg"/>""" +
                    """<img src="/imageserver/%(handle)s/pct:%(x)s,%(y)s,%(w)s,%(h)s/%(width)s,/0/default.jpg"/>""" +
                    """</a>"""
                ) % {
                    "handle": media_handle,
                    "width": width,
                    "x": x1, "y": y1, "w": w, "h": h,
                }
            else:
                return (
                    """<a href="/imageserver/%(handle)s/full/full/0/default.jpg">""" +
                    """<img src="/imageserver/%(handle)s/full/%(width)s,/0/default.jpg"/></a>""") % {
                        "handle": media_handle,
                        "width": width,
                    }
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
        return str(self.instance.gramps_id)
