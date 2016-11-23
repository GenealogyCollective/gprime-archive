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

## Python imports
import os
import base64
import uuid
import crypt
import getpass

## Tornado imports
import tornado.ioloop
from tornado.web import Application, url, StaticFileHandler
from tornado.options import define, options
import tornado.log

## Gramps imports
import gramps.gen.const # initializes locale
from gramps.gen.dbstate import DbState
from gramps.gen.utils.file import media_path_full

## Gramps Connect imports
from gramps_connect.handlers import *
from gramps_connect.forms import *

## Command-line configuration options:
define("hostname", default="localhost",
       help="Name of host Gramps Connect server is running on", type=str)
define("port", default=8000,
       help="Run Gramps Connect server on the given port", type=int)
define("database", default=None,
       help="The Gramps Family Tree to serve", type=str)
define("sitename", default="Gramps Connect",
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

class GrampsConnect(Application):
    """
    Main Gramps Connect webapp class
    """
    def __init__(self, options, settings=None):
        self.options = options
        if settings is None:
            settings = self.default_settings()
        if self.options.database is None:
            raise Exception("Need to specify Gramps Family Tree name with --database='NAME'")
        else:
            self.database = DbState().open_database(self.options.database)
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
                    'path': os.path.join(gramps.gen.const.DATA_DIR, "css"),
                }),
            url(r"/images/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gramps.gen.const.DATA_DIR, "images"),
                }),
            url(r"/misc/(.*)", StaticFileHandler,
                {
                    'path': gramps.gen.const.IMAGE_DIR,
                }),
            url(r"/img/(.*)", StaticFileHandler,
                {
                    'path': os.path.join(gramps.gen.const.PLUGINS_DIR, "webstuff", "img"),
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

if __name__ == "__main__":
    if 'GRAMPS_RESOURCES' not in os.environ:
        os.environ['GRAMPS_RESOURCES'] = os.path.join(
            os.path.abspath(os.path.dirname(gramps.__file__)), "..")
    tornado.options.parse_command_line()
    if options.config:
        tornado.options.parse_config_file(options.config)
    if options.username is None:
        raise Exception("--username=NAME was not provided")
    if options.password is None:
        plaintext = getpass.getpass()
        options.password = crypt.crypt(plaintext)
    tornado.log.logging.info("Gramps Connect starting...")
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
    app = GrampsConnect(options)
    app.listen(options.port)
    tornado.log.logging.info("Starting with the folowing settings:")
    for key in ["port", "home_dir", "hostname", "database", "sitename",
                "debug", "xsrf", "data_dir", "config", "username",
                "password"]:
        tornado.log.logging.info("    " + key + " = " + repr(getattr(options, key)))
    tornado.log.logging.info("  GRAMPS_RESOURCES: " + os.environ['GRAMPS_RESOURCES'])
    tornado.log.logging.info("Control+C to stop server. Running...")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.log.logging.info("Gramps Connect received interrupt...")
    tornado.log.logging.info("Gramps Connect shutting down...")
    if app.database:
        tornado.log.logging.info("Gramps closing database...")
        app.database.close()
