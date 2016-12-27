#
# gPrime - a web-based genealogy program
#
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

## Python imports
import os
import sys
import base64
import uuid
import getpass
import select
import signal
import webbrowser
import threading

from .handlers import *
from .forms import *
from .forms.actionform import import_file
from .passman import password_manager

from tornado.web import Application, url, StaticFileHandler

class GPrimeApp(Application):
    """
    Main webapp class
    """
    def __init__(self, options, database, settings=None):
        import gprime.const
        from gprime.utils.locale import Locale, _
        self.options = options
        if settings is None:
            settings = self.default_settings()
        if options.language is None:
            self.glocale = Locale
            self._ = _
        else:
            self.glocale = Locale(lang=options.language)
            self._ = self.glocale.translation.gettext
        self.database = database
        self.sitename = self.options.sitename
        super().__init__([
            url(r"/", HomeHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="main"),
            url(r'/login', LoginHandler,
                {
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="login"),
            url(r'/logout', LogoutHandler,
                {
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="logout"),
            url(r'/(.*)/(.*)/delete', DeleteHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
            ),
            url(r'/action/?(.*)', ActionHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="action"),
            url(r'/person/?(.*)', PersonHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="person"),
            url(r'/note/?(.*)', NoteHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="note"),
            url(r'/family/?(.*)', FamilyHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="family"),
            url(r'/citation/?(.*)', CitationHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="citation"),
            url(r'/event/?(.*)', EventHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="event"),
            url(r'/media/?(.*)', MediaHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="media"),
            url(r'/place/?(.*)', PlaceHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="place"),
            url(r'/repository/?(.*)', RepositoryHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="repository"),
            url(r'/source/?(.*)', SourceHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="source"),
            url(r'/tag/?(.*)', TagHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="tag"),
            url(r'/imageserver/(.*)', ImageHandler,
                {
                    "database": self.database,
                    "opts" : self.options,
                    "SITE_DIR": self.options.site_dir,
                    "PORT": self.options.port,
                    "HOSTNAME": self.options.hostname,
                    "GET_IMAGE_FN": self.get_image_path_from_handle,
                    "sitename": self.sitename,
                    "glocale": self.glocale,
                    "_": self._,
                },
                name="imageserver",
            ),
            url(r"/json/", JsonHandler,
                {
                    "database": self.database,
                }
            ),
            url(r"/data/(.*)", StaticFileHandler,
                {
                    'path': gprime.const.DATA_DIR,
                }),
            url(r"/css/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gprime.const.DATA_DIR, "css"),
                }),
            url(r"/js/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gprime.const.DATA_DIR, "javascript"),
                }),
            url(r"/images/(.*)", StaticFileHandler,
                {
                    'path': gprime.const.IMAGE_DIR,
                }),
            url(r"/img/(.*)", StaticFileHandler, # CSS images
                {
                    'path': os.path.join(gprime.const.DATA_DIR, "img"),
                }),
        ], **settings)

    def default_settings(self):
        """
        """
        import gprime.const
        return {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url":     "/login",
            'template_path': os.path.join(gprime.const.DATA_DIR, "templates"),
            'debug':         self.options.debug,
            "xsrf_cookies":  self.options.xsrf,
        }

    def get_image_path_from_handle(self, identifier):
        """
        Given an image handle, return the full path/filename.
        """
        from gprime.utils.file import media_path_full
        media = self.database.get_media_from_handle(identifier)
        if media:
            return media_path_full(self.database, media.get_path())
        return ""

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

def main():
    ## Tornado imports
    import tornado.ioloop
    import tornado.log
    from tornado.options import define, options

    ## Command-line configuration options:
    define("hostname", default="localhost",
           help="Name of gPrime server host", type=str)
    define("port", default=8000,
           help="Number of gPrime server port", type=int)
    define("site-dir", default=None,
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
    define("add-user", default=None,
           help="Add a user with password", type=str)
    define("remove-user", default=None,
           help="Remove a user", type=str)
    define("change-password", default=None,
           help="Change a user's password", type=str)
    define("password", default=None,
           help="Give password on command-line (not recommended)", type=str)
    define("server", default=True,
           help="Start the server, True/False", type=bool)
    define("import-file", default=None,
           help="Import a file", type=str)
    define("open-browser", default=True,
           help="Open default web browser", type=bool)
    define("language", default=None,
           help="Language code (eg, 'fr') to use", type=str)

    # Let's go!
    # Really, just need the config-file:
    tornado.options.parse_command_line()
    # Read config-file options:
    if options.config_file:
        tornado.options.parse_config_file(options.config_file)
        # Parse args again, so that command-line options override config-file:
        tornado.options.parse_command_line()
    ################# Process command-line arguments
    if options.site_dir is None:
        raise Exception("--site-dir=NAME was not provided")
    else:
        options.site_dir = os.path.expanduser(options.site_dir)
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
        password_manager.save()
        with open(os.path.join(options.site_dir, "passwd"), "w") as fp:
            fp.write("### This is the password file for gPrime\n")
            fp.write("\n")
    password_manager.load()
    if options.add_user:
        if options.password:
            plaintext = options.password
        else:
            plaintext = getpass.getpass()
        options.server = False
        password_manager.add_user(options.add_user, plaintext)
        password_manager.save()
        ## Initialize user folder:
        os.makedirs(os.path.join(options.site_dir, "users", options.add_user))
    if options.remove_user:
        options.server = False
        password_manager.remove_user(options.remove_user)
        password_manager.save()
    if options.change_password:
        if options.password:
            plaintext = options.password
        else:
            plaintext = getpass.getpass()
        options.server = False
        password_manager.change_password(options.change_password, plaintext)
        password_manager.save()
    ## Open the database:
    database = DbState().open_database(database_dir)
    #options.database = database.get_dbname()
    ## Options after opening:
    if options.import_file:
        options.server = False
        user = User()
        import_file(database, options.import_file, user)
    # Start server up, or exit:
    if not options.server:
        return
    ############################ Starting server:
    define("database", default="Untitled Family Tree", type=str)
    options.database = database.get_dbname()
    tornado.log.logging.info("gPrime starting...")
    if options.debug:
        import tornado.autoreload
        import logging
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        tornado.log.logging.info("Debug mode...")
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
            b = lambda : browser.open("http://%s:%s" % (options.hostname, options.port), new=2)
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
