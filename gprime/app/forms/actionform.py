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

# Python imports:
import time
import os

# Gramps Connect imports:
from .forms import Form, Column, Row

# Gramps imports:
from gprime.cli.plug import BasePluginManager, run_report
from ..dictionarydb import DictionaryDb
from gprime.cli.user import User

# Classes:
class Action(object):
    """
    Object to hold an action (report, export, import, etc)
    """
    def __init__(self, name, ptype, handle):
        self.name = name
        self.ptype = ptype
        self.handle = handle

    @classmethod
    def get_schema(cls):
        return {
            "handle": str,
            "name": str,
            "ptype": str,
        }

    @classmethod
    def get_field_alias(cls, field):
        return field

    def get_field(self, field, db=None, ignore_errors=False):
        if field == "handle":
            return self.handle
        elif field == "name":
            return self.name
        elif field == "ptype":
            return self.ptype

class Table(object):
    """
    Class implementing necessary methods to be a Gramps
    Database Table.
    """
    _class = Action
    count = 0
    _cache = None
    _cache_map = {}

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.get_items() # build cache

    def get_function_dict(self):
        return {
            "class_func": self.get_class(),
            "count_func": self.get_count,
            "commit_func": self.commit,
            "handle_func": self.get_item_by_handle,
            "handles_func": self.get_items,
            "iter_func": self.iter_items,
        }

    def iter_items(self, order_by=None):
        for item in self._cache:
            yield self.get_item_by_handle(item[2])

    def get_class(self):
        return self._class

    def get_item_by_handle(self, handle):
        return Action(*self._cache_map[handle])

    def get_items(self, sort_handles=False):
        if self._cache is None:
            self._cache_map = {}
            pmgr = BasePluginManager.get_instance()
            cl_list = []
            for reg_action in ["get_reg_reports",
                               "get_reg_exporters",
                               "get_reg_importers"]:
                cl_list += getattr(pmgr, reg_action)()
            self._cache = sorted([(pdata.name, self.plugtype(pdata.ptype), pdata.id)
                                  for pdata in cl_list])
            self.count = len(self._cache)
            for items in self._cache:
                self._cache_map[items[2]] = items
        return [x[2] for x in self._cache]

    def plugtype(self, ptype):
        if ptype == 0:
            return "Report"
        elif ptype == 2:
            return "Tool"
        elif ptype == 3:
            return "Import"
        elif ptype == 4:
            return "Export"
        else:
            raise Exception("Not supported")

    def get_count(self):
        return self.count

    def commit(self):
        pass

class ActionForm(Form):
    """
    Form for listing and viewing actions.
    """
    _class = Action
    view = "action"
    tview = "Action"
    table = "Action"

    # URL for page view rows:
    link = "/action/%(handle)s"

    # Search fields to use if not specified:
    default_search_fields = [
        "name",
        "ptype"
    ]

    # Search fields, list is OR
    search_terms = {
        "name": "name",
        "action": "ptype",
    }

    # Fields for page view:
    select_fields = [
        ("name", 50),
        ("ptype", 45),
    ]

    # Other fields needed to select:
    env_fields = [
        "handle"
    ]

    # Does the interator support a sort_handles flag?
    sort = True

    def __init__(self, gramps_database, _, instance=None):
        self.gramps_database = gramps_database
        database = DictionaryDb()
        database.load(None)
        database.add_table_funcs("Action", Table().get_function_dict())
        super().__init__(database, _, instance=instance)

    def set_post_process_functions(self):
        self.post_process_functions = {
        }

    def get_column_labels(self):
        return Row([
            Column("#", self.count_width),
            Column("Name", 50),
            Column("Action", 50),
        ])

    def get_table_count(self):
        return self.database.get_table_func(self.table,"count_func")()

    def get_field_value(self, pid, key):
        options_dict, options_help = self.get_plugin_options(pid)
        return options_dict[key]

    def get_fields(self, pid):
        options_dict, options_help = self.get_plugin_options(pid)
        return options_help

    def get_plugin_options(self, pid):
        """
        Get the default options and help for this plugin.
        """
        pmgr = BasePluginManager.get_instance()
        pdata = pmgr.get_plugin(pid)
        if hasattr(pdata, "optionclass") and pdata.optionclass:
            mod = pmgr.load_plugin(pdata)
            optionclass = getattr(mod, pdata.optionclass)
            optioninstance = optionclass("Name", self.gramps_database)
            optioninstance.load_previous_values()
            return optioninstance.options_dict, optioninstance.options_help
        else:
            return {}, {}

    def describe(self):
        action = self.database.get_table_func("Action", "handle_func")(self.instance.handle)
        return action.name

    def run_action(self, action, handler):
        options, options_help = self.get_plugin_options(action.handle)
        args = {}
        for key, default_value in options.items():
            args[key] = handler.get_argument(key)
        if action.ptype == "Report":
            clr = run_report(self.gramps_database, action.handle, of="/tmp/test.html", off="html", **args)
            # can check for results with clr
        elif action.ptype == "Import":
            filename = download(args["i"], "/tmp/%s-%s-%s.%s" % (str(profile.user.username),
                                                                 str(handle),
                                                                 timestamp(),
                                                                 args["iff"]))
            if filename is not None:
                import_file(self.gramps_database, filename, User()) # callback
        elif action.ptype == "Export":
            pmgr = BasePluginManager.get_instance()
            pdata = pmgr.get_plugin(action.handle)
            export_file(self.gramps_database, "export." + pdata.extension, User()) # callback
        handler.redirect("/action")

## Copied from django-webapp; need to integrate:

def import_file(db, filename, user):
    """
    Import a file (such as a GEDCOM file) into the given db.

    >>> import_file(DbDjango(), "/home/user/Untitled_1.ged", User())
    """
    from gprime.dbstate import DbState
    from gprime.cli.grampscli import CLIManager
    dbstate = DbState()
    climanager = CLIManager(dbstate, setloader=False, user=user) # do not load db_loader
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    # (filename, (exception-type, exception, traceback), pdata)
                    etype, exception, traceback = error_tuple
                    print("ERROR:", name, exception)
                return False
            import_function = getattr(mod, pdata.import_function)
            retval = import_function(db, filename, user)
            return retval
    return False

def download(url, filename=None):
    from urllib.request import Request, urlopen
    from urllib.parse import urlsplit
    import shutil
    def getFilename(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict([x.strip().split('=') if '=' in x else (x.strip(),'')
                                        for x in openUrl.info().split(';')])
            if 'filename' in cd:
                fname = cd['filename'].strip("\"'")
                if fname: return fname
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlsplit(openUrl.url)[2])
    r = urlopen(Request(url))
    success = None
    try:
        filename = filename or "/tmp/%s" % getFilename(url,r)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r,f)
        success = filename
    finally:
        r.close()
    return success

def export_file(db, filename, user):
    """
    Export the db to a file (such as a GEDCOM file).

    >>> export_file(DbDjango(), "/home/user/Untitled_1.ged", User())
    """
    from gprime.dbstate import DbState
    from gprime.cli.grampscli import CLIManager
    dbstate = DbState()
    climanager = CLIManager(dbstate, setloader=False, user=user) # do not load db_loader
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    export_list = pmgr.get_reg_exporters()
    for pdata in export_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    etype, exception, traceback = error_tuple
                    print("ERROR:", name, exception)
                return False
            export_function = getattr(mod, pdata.export_function)
            export_function(db, filename, user)
            return True
    return False
