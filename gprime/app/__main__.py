## Python imports
import os
import base64
import uuid
import crypt
import getpass

## Tornado imports
import tornado.ioloop
from tornado.web import url, StaticFileHandler
from tornado.options import define, options
import tornado.log

## gPrime imports
import gprime.const # initializes locale
from gprime.dbstate import DbState
from gprime.utils.file import media_path_full

from gprime.app.handlers import *
from gprime.app.forms import *
from gprime.app import GPrimeApp

## Command-line configuration options:
define("hostname", default="localhost",
       help="Name of host gPrime server is running on", type=str)
define("port", default=8000,
       help="Run gPrime server on the given port", type=int)
define("database", default=None,
       help="The gPrime Family Tree to serve", type=str)
define("sitename", default="gPrime",
       help="Name to appear on all pages", type=str)
define("debug", default=False,
       help="Tornado debug", type=bool)
define("xsrf", default=True,
       help="Use xsrf cookie", type=bool)
define("data_dir", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
       help="Base directory (where static, templates, etc. are)", type=str)
define("home_dir", default=os.path.expanduser("~/.gramps/"),
       help="Home directory for media", type=str)
define("config", default=None,
       help="Config file of options", type=str)
define("username", default=None,
       help="Login username", type=str)
define("password", default=None,
       help="Login encrypted password", type=str)

tornado.options.parse_command_line()
if options.config:
    tornado.options.parse_config_file(options.config)
if options.username is None:
    raise Exception("--username=NAME was not provided")
if options.password is None:
    plaintext = getpass.getpass()
    options.password = crypt.crypt(plaintext)
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
app = GPrimeApp(options)
app.listen(options.port)
tornado.log.logging.info("Starting with the folowing settings:")
for key in ["port", "home_dir", "hostname", "database", "sitename",
            "debug", "xsrf", "data_dir", "config", "username",
            "password"]:
    tornado.log.logging.info("    " + key + " = " + repr(getattr(options, key)))
tornado.log.logging.info("Control+C to stop server. Running...")
try:
    tornado.ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    tornado.log.logging.info("gPrime received interrupt...")
tornado.log.logging.info("gPrime shutting down...")
if app.database:
    tornado.log.logging.info("gPrime closing database...")
    app.database.close()
