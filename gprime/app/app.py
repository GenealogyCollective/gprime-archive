## Python imports
import os
import sys
import base64
import uuid
from passlib.hash import sha256_crypt as crypt
import getpass
import select
import signal
import webbrowser
import threading

## gPrime imports
import gprime.const # initializes locale
from gprime.dbstate import DbState
from gprime.utils.file import media_path_full
from gprime.cli.user import User

from .handlers import *
from .forms import *
from .forms.actionform import import_file

from tornado.web import Application, url, StaticFileHandler

class GPrimeApp(Application):
    """
    Main webapp class
    """
    def __init__(self, options, database, settings=None):
        self.options = options
        if settings is None:
            settings = self.default_settings()
        if database is None:
            raise Exception("Need to specify Family Tree name with --database='NAME'")
        else:
            self.database = database
        if self.database is None:
            raise Exception("Unable to open database '%s'" % self.options.database)
        self.sitename = self.options.sitename
        super().__init__([
            url(r"/", HomeHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="main"),
            url(r'/login', LoginHandler,
                {
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="login"),
            url(r'/logout', LogoutHandler,
                {
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="logout"),
            url(r'/(.*)/(.*)/delete', DeleteHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
            ),
            url(r'/action/?(.*)', ActionHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="action"),
            url(r'/person/?(.*)', PersonHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="person"),
            url(r'/note/?(.*)', NoteHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="note"),
            url(r'/family/?(.*)', FamilyHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="family"),
            url(r'/citation/?(.*)', CitationHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="citation"),
            url(r'/event/?(.*)', EventHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="event"),
            url(r'/media/?(.*)', MediaHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="media"),
            url(r'/place/?(.*)', PlaceHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="place"),
            url(r'/repository/?(.*)', RepositoryHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="repository"),
            url(r'/source/?(.*)', SourceHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="source"),
            url(r'/tag/?(.*)', TagHandler,
                {
                    "database": self.database,
                    "sitename": self.sitename,
                    "opts" : self.options,
                },
                name="tag"),
            url(r'/imageserver/(.*)', ImageHandler,
                {
                    "database": self.database,
                    "opts" : self.options,
                    "HOMEDIR": self.options.home_dir,
                    "PORT": self.options.port,
                    "HOSTNAME": self.options.hostname,
                    "GET_IMAGE_FN": self.get_image_path_from_handle,
                    "sitename": self.sitename,
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
                    'path': self.options.data_dir,
                }),
            url(r"/css/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gprime.const.DATA_DIR, "css"),
                }),
            url(r"/images/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gprime.const.DATA_DIR, "images"),
                }),
            url(r"/misc/(.*)", StaticFileHandler,
                {
                    'path': gprime.const.IMAGE_DIR,
                }),
            url(r"/img/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gprime.const.PLUGINS_DIR, "webstuff", "img"),
                }),
        ], **settings)

    def default_settings(self):
        """
        """
        return {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url":     "/login",
            'template_path': os.path.join(self.options.data_dir, "templates"),
            'debug':         self.options.debug,
            "xsrf_cookies":  self.options.xsrf,
        }

    def get_image_path_from_handle(self, identifier):
        """
        Given an image handle, return the full path/filename.
        """
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
    define("database", default=None,
           help="The gPrime Family Tree database to serve", type=str)
    define("sitename", default="gPrime",
           help="Name to appear on all pages", type=str)
    define("debug", default=False,
           help="Set debugging on/off", type=bool)
    define("xsrf", default=True,
           help="Use xsrf cookie", type=bool)
    define("data-dir", default=gprime.const.DATA_DIR,
           help="Base directory (where static, templates, etc. are)", type=str)
    define("home-dir", default=gprime.const.HOME_DIR,
           help="Home directory", type=str)
    define("config", default=None,
           help="Config file of gPrime options", type=str)
    define("username", default=None,
           help="Login username", type=str)
    define("password-hash", default=None,
           help="Encrypted login password", type=str)
    define("create", default=None,
           help="Create a database directory", type=str)
    define("server", default=True,
           help="Start the server", type=bool)
    define("import-file", default=None,
           help="Import a file", type=str)
    define("open-browser", default=True,
           help="Open default web browser", type=bool)

    # Let's go!
    tornado.options.parse_command_line()
    # Handle standard options:
    if options.config:
        tornado.options.parse_config_file(options.config)
    if options.username is None:
        raise Exception("--username=NAME was not provided")
    if options.password_hash is None:
        plaintext = getpass.getpass()
        options.password_hash = crypt.hash(plaintext)
    ### Handle database options:
    if options.create:
        DbState().create_database(options.create)
    ## Open the database:
    database = DbState().open_database(options.database)
    # If database was a filename, set it to dbname:
    if database:
        options.database = database.get_dbname()
    ## Options after opening:
    if options.import_file:
        user = User()
        import_file(database, options.import_file, user)
    # Start server up, or exit:
    if not options.server:
        return
    tornado.log.logging.info("gPrime starting...")
    if options.debug:
        import tornado.autoreload
        import logging
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        tornado.log.logging.info("Debug mode...")
        directory = options.data_dir
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
    for key in ["port", "home_dir", "hostname", "database", "sitename",
                "debug", "xsrf", "data_dir", "config", "username",
                "password_hash"]:
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
