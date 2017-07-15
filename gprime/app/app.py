#
# gPrime - a web-based genealogy program
#
# Copyright (c) 2016-2017 gPrime Development Team
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

## Python imports
import re
import os
import sys
import base64
import uuid
import getpass
import select
import signal
import shutil
import webbrowser
import threading
from passlib.hash import sha256_crypt as crypt
from collections import defaultdict

from .handlers import *
from .forms import *
from .forms.actionform import import_file
from ..db import DbTxn
from ..version import VERSION

from tornado.web import Application, url, StaticFileHandler

try:
    crypt.hash("")
except AttributeError:
    crypt.hash = crypt.encrypt

def make_path_relative(filename):
    """
    Given a filename, make it relative.
    """
    parts = re.split(r"[\\/]", filename)
    if ":" in parts[0]:
        return "/".join(
            [p for p in parts[0].split(":")[1:] + parts[1:] if p])
    else:
        return "/".join([p for p in parts if p])

def get_image_path_from_media(database, media):
    from gprime.utils.file import media_path_full
    if media:
        return media_path_full(database, media.get_path())
    return ""

class GPrimeApp(Application):
    """
    Main webapp class
    """
    def __init__(self, options, database, **kwargs):
        import gprime.const
        self.options = options
        self.prefix = self.options.prefix
        self.user_data = {} # user to user_data map
        self.database = database
        self.sitename = options.sitename
        settings = kwargs
        settings.update(self.default_settings())
        handlers = [
            (self.make_url(r"/(.*)/attribute_list/(.*)"),
             AttributeHandler, "attribute_list", self.make_env({})),
            (self.make_url(r"/(.*)/address_list/(.*)"),
             AddressHandler, "address_list", self.make_env({})),
            (self.make_url(r"/(.*)/lds_ord_list/(.*)"),
             LDSHandler, "lds_ord_list", self.make_env({})),
            (self.make_url(r"/(.*)/urls/(.*)"),
             URLHandler, "urls", self.make_env({})),
            (self.make_url(r"/(.*)/media_list/(.*)"),
             MediaRefHandler, "media_list", self.make_env({})),
            (self.make_url(r"/(.*)/child_ref_list/(.*)"),
             ChildRefHandler, "child_ref_list", self.make_env({})),
            (self.make_url(r"/(.*)/event_ref_list/(.*)"),
             EventRefHandler, "event_ref_list", self.make_env({})),
            (self.make_url(r"/(.*)/person_ref_list/(.*)"),
             PersonRefHandler, "person_ref_list", self.make_env({})),
            (self.make_url(r"/(.*)/placeref_list/(.*)"),
             PlaceRefHandler, "placeref_list", self.make_env({})),
            (self.make_url(r"/(.*)/reporef_list/(.*)"),
             RepoRefHandler, "reporef_list", self.make_env({})),
            (self.make_url(r"/"),
             HomeHandler, "main", self.make_env({})),
            (self.make_url(r'/settings'),
             SettingsHandler, "settings", self.make_env({})),
            (self.make_url(r'/login'),
             LoginHandler, "login", self.make_env({})),
            (self.make_url(r'/logout'),
             LogoutHandler, "logout", self.make_env({})),
            (self.make_url(r'/action/?(.*)'),
             ActionHandler, "action", self.make_env({})),
            (self.make_url(r'/person/(.*)/name/(.*)/surname/(.*)'),
             SurnameHandler, "surname", self.make_env({})),
            (self.make_url(r'/person/(.*)/name/(.*)/?(.*)'),
             NameHandler, "name", self.make_env({})),
            (self.make_url(r'/person/?(.*)'),
             PersonHandler, "person", self.make_env({})),
            (self.make_url(r'/note/?(.*)'),
             NoteHandler, "note", self.make_env({})),
            (self.make_url(r'/family/?(.*)'),
             FamilyHandler, "family", self.make_env({})),
            (self.make_url(r'/citation/?(.*)'),
             CitationHandler, "citation", self.make_env({})),
            (self.make_url(r'/event/?(.*)'),
             EventHandler, "event", self.make_env({})),
            (self.make_url(r'/media/?(.*)'),
             MediaHandler, "media", self.make_env({})),
            (self.make_url(r'/place/?(.*)'),
             PlaceHandler, "place", self.make_env({})),
            (self.make_url(r'/repository/?(.*)'),
             RepositoryHandler, "repository", self.make_env({})),
            (self.make_url(r'/source/?(.*)'),
             SourceHandler, "source", self.make_env({})),
            (self.make_url(r'/tag/?(.*)'),
             TagHandler, "tag", self.make_env({})),
            (self.make_url(r'/imageserver/(.*)'),
             ImageHandler, "imageserver", self.make_env({
                "SITE_DIR": self.options.site_dir,
                "PORT": self.options.port,
                "HOSTNAME": self.options.hostname,
                "GET_IMAGE_FN": self.get_image_path_from_handle,
            })),
            (self.make_url(r"/json/"),
             JsonHandler, "json", self.make_env({})),
            (self.make_url(r"/data/(.*)"),
             StaticFileHandler, "data", {
                'path': gprime.const.DATA_DIR,
            }),
            (self.make_url(r"/css/(.*)"),
             StaticFileHandler, "css", {
                'path': os.path.join(gprime.const.DATA_DIR, "css"),
            }),
            (self.make_url(r"/js/(.*)"),
             StaticFileHandler, "javascript", {
                'path': os.path.join(gprime.const.DATA_DIR, "javascript"),
            }),
            (self.make_url(r"/images/(.*)"),
             StaticFileHandler, "images", {
                'path': gprime.const.IMAGE_DIR,
            }),
            (self.make_url(r"/img/(.*)"),
             StaticFileHandler, "css_img", {
                'path': os.path.join(gprime.const.DATA_DIR, "img"),
            }),
            (self.make_url(r"/(.*)"),
             My404Handler, "my404", self.make_env({})),
        ]
        super().__init__([url(handler[0],
                              handler[1],
                              handler[3],
                              name=handler[2])
                          for handler in handlers], **settings)

    def make_url(self, pattern):
        if pattern == "/" and self.prefix:
            return self.prefix
        else:
            return "%s%s" % (self.prefix, pattern)

    def make_env(self, handler_env):
        env = {
            "database": self.database,
            "sitename": self.sitename,
            "opts" : self.options,
            "app": self,
        }
        env.update(handler_env)
        return env

    def clear_user_data(self, user):
        if user in self.user_data:
            del self.user_data[user]

    def get_translate_func(self, user):
        from gprime.utils.locale import Locale, _
        def func(*args, **kwargs):
            if user not in self.user_data:
                try:
                    user_data = self.database.get_user_data(user)
                except:
                    user_data = {}
                if user_data:
                    self.user_data[user] = user_data
                else:
                    self.user_data[user] = {}
            if "language" in self.user_data[user] and self.user_data[user]["language"]:
                self.user_data[user]["glocale"] = Locale(lang=self.user_data[user]["language"])
                self.user_data[user]["_"] = self.user_data[user]["glocale"].translation.gettext
            else:
                self.user_data[user]["language"] = "en"
                self.user_data[user]["glocale"] = Locale
                self.user_data[user]["_"] = _
            return self.user_data[user]["_"](*args, **kwargs)
        return func

    def get_css(self, user):
        if user not in self.user_data:
            try:
                user_data = self.database.get_user_data(user)
            except:
                user_data = {}
            if user_data:
                self.user_data[user] = user_data
            else:
                self.user_data[user] = {}
        if "css" in self.user_data[user]:
            if not self.user_data[user]["css"]:
                self.user_data[user]["css"] = "Web_Mainz.css"
        else:
            self.user_data[user]["css"] = "Web_Mainz.css"
        return self.user_data[user]["css"]

    def get_permissions(self, user):
        if user not in self.user_data:
            try:
                user_data = self.database.get_user_data(user)
            except:
                user_data = {}
            if user_data:
                self.user_data[user] = user_data
            else:
                self.user_data[user] = {}
        if "permissions" in self.user_data[user]:
            if not self.user_data[user]["permissions"]:
                self.user_data[user]["permissions"] = set()
        else:
            self.user_data[user]["permissions"] = set()
        return self.user_data[user]["permissions"]

    def can_add(self, user):
        return "add" in self.get_permissions(user)

    def can_edit(self, user):
        return "edit" in self.get_permissions(user)

    def can_delete(self, user):
        return "delete" in self.get_permissions(user)

    def is_admin(self, user):
        return "admin" in self.get_permissions(user)

    def default_settings(self):
        """
        """
        import gprime.const
        return {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url":     self.make_url("/login"),
            'template_path': os.path.join(gprime.const.DATA_DIR, "templates"),
            'debug':         self.options.debug,
            "xsrf_cookies":  self.options.xsrf,
        }

    def get_image_path_from_handle(self, identifier):
        """
        Given an image handle, return the full path/filename.
        """
        media = self.database.get_media_from_handle(identifier)
        return get_image_path_from_media(self.database, media)

    def get_object_from_url(self, prefix):
        if prefix.count("/") == 1:
            view, handle = prefix.split("/", 1)
        elif prefix.count("/") > 1:
            view, handle, extra = prefix.split("/", 2)
        obj = self.database.get_table_func(view.title(), "handle_func")(handle)
        return obj

    def server_info(self):
        """
        Return the server url information
        """
        return "The gPrime server is running at: %s:" % (self.options.host,
                                                         self.options.port)

    def _signal_info(self, sig, frame):
        print(self.server_info())

    def init_signal(self):
        if not sys.platform.startswith('win') and sys.stdin.isatty():
            signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._signal_stop)
        if hasattr(signal, 'SIGUSR1'):
            # Windows doesn't support SIGUSR1
            signal.signal(signal.SIGUSR1, self._signal_info)
        if hasattr(signal, 'SIGINFO'):
            # only on BSD-based systems
            signal.signal(signal.SIGINFO, self._signal_info)

    def _handle_sigint(self, sig, frame):
        """
        SIGINT handler spawns confirmation dialog
        """
        # register more forceful signal handler for ^C^C case
        signal.signal(signal.SIGINT, self._signal_stop)
        # request confirmation dialog in bg thread, to avoid
        # blocking the App
        thread = threading.Thread(target=self._confirm_exit)
        thread.daemon = True
        thread.start()

    def _restore_sigint_handler(self):
        """callback for restoring original SIGINT handler"""
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _confirm_exit(self):
        """
        confirm shutdown on ^C

        A second ^C, or answering 'y' within 5s will cause shutdown,
        otherwise original SIGINT handler will be restored.

        This doesn't work on Windows.
        """
        info = tornado.log.logging.info
        info('interrupted')
        sys.stdout.write("Shutdown the gPrime server (y/[n])? ")
        sys.stdout.flush()
        r,w,x = select.select([sys.stdin], [], [], 5)
        if r:
            line = sys.stdin.readline()
            if line.lower().startswith('y') and 'n' not in line.lower():
                tornado.log.logging.critical("Shutdown confirmed")
                tornado.ioloop.IOLoop.current().stop()
                return
        else:
            print("No answer for 5s:", end=' ')
        print("resuming operation...")
        # no answer, or answer is no:
        # set it back to original SIGINT handler
        # use IOLoop.add_callback because signal.signal must be called
        # from main thread
        tornado.ioloop.IOLoop.current().add_callback(self._restore_sigint_handler)

    def _signal_stop(self, sig, frame):
        tornado.log.logging.critical("received signal %s, stopping", sig)
        tornado.ioloop.IOLoop.current().stop()

    def _restore_sigint_handler(self):
        """
        callback for restoring original SIGINT handler
        """
        signal.signal(signal.SIGINT, self._handle_sigint)

def run_app():
    ## Tornado imports
    import tornado.ioloop
    import tornado.log
    from tornado.options import define, options

    ## Command-line configuration options:
    define("hostname", default="localhost",
           help="Name of gPrime server host", type=str)
    define("port", default=8000,
           help="Number of gPrime server port", type=int)
    define("site-dir", default="gprime-site",
           help="The gPrime site directory to use", type=str)
    define("sitename", default="gPrime",
           help="Name to appear on all web pages", type=str)
    define("debug", default=False,
           help="Set debugging True/False", type=bool)
    define("xsrf", default=True,
           help="Use xsrf cookie, True/False", type=bool)
    define("config-file", default=None,
           help="Config file of gPrime options", type=str)
    define("create", default=None,
           help="Create a site directory (given by --site-dir) with this Family Tree name", type=str)
    define("add-user", default=False,
           help="Add a user; requires --user; optional --password and --permissions", type=bool)
    define("remove-user", default=False,
           help="Remove a user; requires --user=USERNAME", type=bool)
    define("change-password", default=False,
           help="Change a user's password; requires --user=USERNAME", type=bool)
    define("password", default=None,
           help="Give password on command-line (not recommended)", type=str)
    define("permissions", default=None,
           help="User permissions (edit, delete, add, admin)", type=str)
    define("user", default=None,
           help="User for change-password, add-user, remove-user, or permissions", type=str)
    define("server", default=True,
           help="Start the server, True/False", type=bool)
    define("import-file", default=None,
           help="Import a file", type=str)
    define("import-media", default=True,
           help="Attempt to import associated media with --import-file", type=bool)
    define("open-browser", default=True,
           help="Open default web browser", type=bool)
    define("prefix", default="",
           help="Site URL prefix", type=str)
    define("version", default=False,
           help="Show the version of gprime (%s)" % VERSION, type=bool)
    define("info", default=False,
           help="Show information about the database", type=bool)
    # Let's go!
    # Really, just need the config-file:
    tornado.options.parse_command_line()
    # Read config-file options:
    if options.config_file:
        tornado.options.parse_config_file(options.config_file)
        # Parse args again, so that command-line options override config-file:
        tornado.options.parse_command_line()
    ################# Process command-line arguments
    if options.version:
        print("gPrime version is: %s" % VERSION)
        sys.exit(0)
    options.site_dir = os.path.expanduser(options.site_dir)
    # Use site-dir/config.cfg if one, and not overridden on command line:
    default_config_file = os.path.join(options.site_dir, "config.cfg")
    if options.config_file is None and os.path.exists(default_config_file):
        old_site_dir = options.site_dir
        tornado.options.parse_config_file(default_config_file)
        if options.site_dir != old_site_dir:
            tornado.log.logging.warning("Ignoring site_dir = %s in config.cfg...", repr(options.site_dir))
        # Parse args again, so that command-line options override config-file:
        tornado.options.parse_command_line()
        options.site_dir = old_site_dir # make sure this is not overridden
    if options.debug:
        import logging
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        tornado.log.logging.info("Debug mode...")
    # Handle gPrime intialization:
    import gprime.const # initializes locale
    gprime.const.set_site_dir(options.site_dir) ## when we don't have options
    from gprime.dbstate import DbState
    from gprime.cli.user import User
    ### Handle site options:
    database_dir = os.path.join(options.site_dir, "database")
    users_dir = os.path.join(options.site_dir, "users")
    media_dir = os.path.join(options.site_dir, "media")
    media_cache_dir = os.path.join(options.site_dir, "media", "cache")
    if options.create:
        options.server = False
        # Make the site_dir:
        os.makedirs(options.site_dir)
        # Make the database:
        DbState().create_database(database_dir, options.create)
        # Make the user folders:
        os.makedirs(users_dir)
        # Make the media folder:
        os.makedirs(media_dir)
        os.makedirs(media_cache_dir)
        # Make an image-missing.png default:
        shutil.copy(os.path.join(gprime.const.IMAGE_DIR, "image-missing.png"),
                    os.path.join(media_dir, "image-missing.png"))
    ## Open the database:
    database = DbState().open_database(database_dir)
    if options.add_user:
        options.server = False
        if options.user is None:
            raise Exception("Missing --user=USERNAME")
        if options.password:
            plaintext = options.password
        else:
            plaintext = getpass.getpass()
        options.server = False
        if options.permissions:
            permissions = {code.strip().lower() for code in options.permissions.split(",")}
        else:
            permissions = {"add", "edit", "delete"}
        ## Initialize user folder:
        try:
            os.makedirs(os.path.join(options.site_dir, "users", options.user))
        except:
            pass
        database.add_user(username=options.user,
                          password=crypt.hash(plaintext),
                          permissions=permissions,
                          data={}) # could set css here
    elif options.remove_user:
        options.server = False
        if options.user is None:
            raise Exception("Missing --user=USERNAME")
        options.server = False
        database.remove_user(username=options.user)
    elif options.change_password:
        options.server = False
        if options.user is None:
            raise Exception("Missing --user=USERNAME")
        if options.password:
            plaintext = options.password
        else:
            plaintext = getpass.getpass()
        options.server = False
        if options.permissions:
            permissions = {code.strip().lower() for code in options.permissions.split(",")}
            database.update_user_data(username=options.user,
                                      data={"password": crypt.hash(plaintext),
                                            "permissions": permissions})
        else:
            database.update_user_data(username=options.user,
                                      data={"password": crypt.hash(plaintext)})
    elif options.permissions:
        options.server = False
        if options.user is None:
            raise Exception("Missing --user=USERNAME")
        permissions = {code.strip().lower() for code in options.permissions.split(",")}
        database.update_user_data(username=options.user,
                                  data={"permissions": permissions})
    elif options.password:
        raise Exception("Missing --change-password --user=USERNAME")
    ## Options after opening:
    if options.info:
        options.server = False
        users = database.get_users()
        for user in users:
            print("%s:" % user)
            data = database.get_user_data(user)
            for key in data:
                print("    %s: %s" % (key, data[key]))
    elif options.import_file:
        options.server = False
        user = User()
        options.import_file = os.path.expanduser(options.import_file)
        import_file(database, options.import_file, user)
        # copy images to media subdirectory
        if options.import_media:
            media_dir = os.path.join(options.site_dir, "media")
            media_copies = set()
            with DbTxn("gPrime initial import", database) as transaction:
                for media in database.iter_media():
                    if media.path == "image-missing.png":
                        continue # already there
                    src = get_image_path_from_media(database, media)
                    relative = make_path_relative(media.path)
                    dst = os.path.join(media_dir, relative)
                    if not os.path.exists(src):
                        # try where import-file was
                        src = os.path.join(os.path.dirname(options.import_file),
                                           relative)
                    if os.path.exists(src):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        if dst not in media_copies:
                            shutil.copy(src, dst)
                            tornado.log.logging.info("Media copied to `%s`" % dst)
                            media_copies.add(dst)
                        media.path = relative
                        database.commit_media(media, transaction)
                    else:
                        tornado.log.logging.warning("Media file not found: `%s`" % media.path)
                database.set_mediapath(os.path.abspath(media_dir)) # relative or absolute
    # Start server up, or exit:
    if not options.server:
        database.close()
        return
    ############################ Starting server:
    media_dir = os.path.join(options.site_dir, "media")
    database.set_mediapath(os.path.abspath(media_dir)) # relative or absolute
    define("database", default="Untitled Family Tree", type=str)
    options.database = database.get_dbname()
    tornado.log.logging.info("gPrime starting...")
    if options.debug:
        import tornado.autoreload
        directory = gprime.const.DATA_DIR
        template_directory = os.path.join(directory, 'templates')
        tornado.log.logging.info(template_directory)
        for dirpath, dirnames, filenames in os.walk(template_directory):
            for filename in filenames:
                template_filename = os.path.join(dirpath, filename)
                tornado.log.logging.info("   watching: " + os.path.relpath(template_filename))
                tornado.autoreload.watch(template_filename)
    app = GPrimeApp(options, database)
    app.listen(options.port)
    tornado.log.logging.info("Starting with the folowing settings:")
    tornado.log.logging.info("    DATA_DIR = " + gprime.const.DATA_DIR)
    tornado.log.logging.info("    serving  = http://%s:%s%s" % (options.hostname, options.port, options.prefix))
    for key in ["port", "site_dir", "hostname", "sitename",
                "debug", "xsrf", "config_file"]:
        tornado.log.logging.info("    " + key + " = " + repr(getattr(options, key)))
    tornado.log.logging.info("Control+C twice to stop server. Running...")
    # Open up a browser window:
    if options.open_browser:
        try:
            browser = webbrowser.get(None)
        except webbrowser.Error as e:
            tornado.log.logging.warning('No web browser found: %s.' % e)
            browser = None
        if browser:
            b = lambda : browser.open("http://%s:%s%s" % (options.hostname, options.port, app.make_url("/")), new=2)
            threading.Thread(target=b).start()

    app.init_signal()

    if sys.platform.startswith('win'):
        # add no-op to wake every 5s
        # to handle signals that may be ignored by the inner loop
        pc = tornado.ioloop.PeriodicCallback(lambda : None, 5000)
        pc.start()

    # Start Tornado server:
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.log.logging.info("gPrime received interrupt...")
    tornado.log.logging.info("gPrime shutting down...")
    if app.database:
        tornado.log.logging.info("gPrime closing database...")
        app.database.close()

def main():
    from tornado.options import options
    import traceback
    try:
        run_app()
    except Exception as exc:
        if options.debug:
            traceback.print_exc()
        else:
            print(exc)
