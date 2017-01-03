#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2015-2016 Douglas S. Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

## This file is copied from gprime/plugins/db/dbapi/settings.py
## into each SITE-DIR/database directory. You can edit each copy
## to connect to different databases, or with different
## parameters.

import os

from gprime.plugins.db.dbapi.sqlite import Sqlite
path_to_db = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'sqlite.db')
dbapi = Sqlite(path_to_db)

# Edit this file to use other SQL databases:

# dbname = "mydatabase"
# host = "localhost"
# user = "username"
# password = "password"
# port = "8000"

# from gprime.plugins.db.dbapi.mysql import MySQL
# dbapi = MySQL(host, user, password, dbname,
#               charset='utf8', use_unicode=True)

# from gprime.plugins.db.dbapi.postgresql import Postgresql
# dbapi = Postgresql(dbname=dbname, user=user,
#                    host=host, password=password)
