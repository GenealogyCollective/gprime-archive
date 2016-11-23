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

import tornado.web
import simplejson

from .handlers import BaseHandler

class JsonHandler(BaseHandler):
    """
    Process an Ajax/Json query request.
    """
    @tornado.web.authenticated
    def get(self):
        field = self.get_argument("field", None)
        query = self.get_argument("q", "").strip()
        page = int(self.get_argument("p", "1"))
        size = int(self.get_argument("s", "10"))
        if field in ["mother", "father"]:
            table = "Person"
            fields = ["primary_name.first_name",
                      "primary_name.surname_list.0.surname",
                      "gender",
                      "handle"]
            order_by = [('primary_name.surname_list.0.surname', "ASC"),
                        ('primary_name.first_name', "ASC")]
            if "," in query:
                surname, given = [s.strip() for s in query.split(",", 1)]
                where = ["AND", [("primary_name.surname_list.0.surname", "LIKE", "%s%%" % surname),
                                 ("primary_name.first_name", "LIKE", "%s%%" % given),
                             ]]
            elif query:
                where = ("primary_name.surname_list.0.surname", "LIKE", "%s%%" % query)
            else:
                where = None
            # UNKNOWN = 2, MALE = 1, FEMALE = 0
            if field == "mother":
                if where:
                    where = ["AND", [where, ("gender", "IN", [0, 2])]]
                else:
                    where = ("gender", "=", 0)
            elif field == "father":
                if where:
                    where = ["AND", [where, ("gender", "IN", [1, 2])]]
                else:
                    where = ("gender", "=", 1)
            return_fields = ['primary_name.surname_list.0.surname',
                             'primary_name.first_name']
            return_delim = ", "
        elif field == "person":
            pass
        elif field == "place":
            pass
        else:
            raise Exception("""Invalid field: '%s'; Example: /json/?field=mother&q=Smith&p=1&size=10""" % field)
        ## ------------
        self.log.debug("received json query: " + str(where))
        queryset = self.database.get_queryset_by_table_name(table)
        queryset.limit(start=(page - 1) * size, count=size)
        queryset.where_by = where
        queryset.order_by = order_by
        class Result(list):
            total = 0
        rows = Result(queryset.select("handle", *return_fields))
        queryset = self.database.get_queryset_by_table_name(table)
        queryset.where_by = where
        rows.total = queryset.count()
        response_data = {"results": [], "total": rows.total}
        for row in rows:
            name = return_delim.join([row[f] for f in return_fields])
            response_data["results"].append({"id": row["handle"],
                                             "name": name})
        self.set_header('Content-Type', 'application/json')
        self.write(simplejson.dumps(response_data))
