
from tornado.web import Application

class GPrimeApp(Application):
    """
    Main webapp class
    """
    def __init__(self, options, settings=None):
        self.options = options
        if settings is None:
            settings = self.default_settings()
        if self.options.database is None:
            raise Exception("Need to specify Family Tree name with --database='NAME'")
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

