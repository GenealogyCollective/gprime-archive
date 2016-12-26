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

## Based on:
## https://github.com/IIIF/image-api/blob/master/implementations/pi3f/pi3f_21.py

import tornado

import os
import json
import urllib
import glob
import hashlib
import io
import re
from PIL import Image

from .handlers import BaseHandler

class Abort(Exception):
    """
    Base class for aborting execution.
    """

class Abort501(Abort):
    """
    Error 501 class for aborting execution.
    """

class Abort400(Abort):
    """
    Error 400 class for aborting execution.
    """

class Abort401(Abort):
    """
    Error 401 class for aborting execution.
    """

class Abort404(Abort):
    """
    Error 404 class for aborting execution.
    """

class ImageFile(object):
    def __init__(self, filename, identifier, application):
        self.filename = filename
        self.identifier = identifier
        self.cacher = application.cacher
        self.config = application.config
        self.image = None

        self.height = 0
        self.width = 0
        self.qualities = []
        self.formats = []

    def open(self):
        if self.image != None:
            return self.image
        try:
            img = Image.open(self.filename)
        except:
            raise Abort501(self.identifier.make_error_message("Cannot open file"))
        (imageW, imageH) = img.size
        self.height = imageH
        self.width = imageW
        self.image = img
        return img

    def close(self):
        self.image.close()
        self.image = None

    def process(self, ir):
        image = self.open()
        cf = self.config
        if self.identifier.value.endswith(cf.DEGRADED_IDENTIFIER):
            if cf.DEGRADED_SIZE > 0:
                # resize max size
                image = image.resize(self.degradedWidth, self.degradedHeight)
            if cf.DEGRADED_QUALITY:
                nquality = {'gray':'L','bitonal':'1'}[cf.DEGRADED_QUALITY]
                image = image.convert(nquality)

        # region
        if (ir.region.width != self.width or ir.region.height != self.height):
            box = (ir.region.x,ir.region.y,ir.region.x+ir.region.width,ir.region.y+ir.region.height)
            image = image.crop(box)
        # size
        if ir.size.width != ir.region.width or ir.size.height != ir.region.height:
            image = image.resize((ir.size.width, ir.size.height))
        # rotation
        if ir.rotation.mirror:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if ir.rotation.rotation != 0:
            # NB Rotation in PIL can introduce extra pixels on edges, even for square
            # PIL is counter-clockwise, so need to reverse
            rot = 360 - ir.rotation.rotation
            try:
                image = image.rotate(rot, expand=1)
            except:
                # old version of PIL without expand
                segx = image.size[0]
                segy = image.size[1]
                angle = radians(rot)
                rx = abs(segx*cos(angle)) + abs(segy*sin(angle))
                ry = abs(segy*cos(angle)) + abs(segx*sin(angle))

                bg = Image.new("RGB", (rx,ry), (0,0,0))
                tx = int((rx-segx)/2)
                ty = int((ry-segy)/2)
                bg.paste(image, (tx,ty,tx+segx,ty+segy))
                image = bg.rotate(rot)

        # quality
        if ir.quality.value != 'default':
            nquality = {'color':'RGB','gray':'L','bitonal':'1'}[ir.quality.value]
            image = image.convert(nquality)

        nformat = ir.format.value.upper()
        if nformat == 'JPG':
            nformat = 'JPEG'
        elif nformat == "TIF":
            nformat = "TIFF"
        # Can't save alpha mode in jpeg
        if nformat == 'JPEG' and image.mode == 'P':
            image = image.convert('RGB')

        output = io.BytesIO()
        try:
            image.save(output,format=nformat, quality=cf.jpegQuality)
        except SystemError:
            raise Abort400(imageRequest.size.make_error_message('Unsupported size... tile cannot extend outside image'))
        except IOError:
            raise Abort501(imageRequest.format.make_error_message('Unsupported output format for base image'))
        contents = output.getvalue()
        output.close()
        self.cacher.cache(ir.canonical, contents)

    def cache_info(self):
        # NB need to cache from the *full* image
        if not self.height:
            cacher = self.cacher
            path = self.identifier.value + "/info.json"
            if cacher.exists(path):
                data = cacher.fetch(path)
                info = json.loads(data)
                self.height = info['height']
                self.width = info['width']
                self.qualities = info['profile'][1]['qualities']
            else:
                self.make_info()

    def make_info(self):
        if not self.height:
            image = self.open()
        (imageW, imageH) = (self.width, self.height)

        cf = self.config
        if cf.DEGRADE_IMAGES and self.identifier.value.endswith(cf.DEGRADED_IDENTIFIER) and cf.DEGRADED_SIZE:
            # Make max 400 on long edge and add in auth service
            if imageW > imageH:
                ratio = float(cf.DEGRADED_SIZE) / imageW
                imageH = int(imageH * ratio)
                imageW = cf.DEGRADED_SIZE
            else:
                ratio = float(cf.DEGRADED_SIZE) / imageH
                imageW = int(imageW * ratio)
                imageH = cf.DEGRADED_SIZE

            self.degradedWidth = imageW
            self.degradedHeight = imageH

        all_scales = []
        sfn = 0
        sf = 1
        while float(imageH)/sf > cf.MIN_SIZE and float(imageW)/sf > cf.MIN_SIZE:
            all_scales.append(sf)
            sfn += 1
            sf = 2**sfn

        if image.mode == '' or (cf.DEGRADE_IMAGES and cf.DEGRADED_QUALITY == 'bitonal'):
            qualities = []
        elif image.mode == 'L' or (cf.DEGRADE_IMAGES and cf.DEGRADED_QUALITY == 'gray'):
            qualities = ['gray']
        else:
            qualities = ['color','gray']
        self.qualities = qualities

        sizes = []
        for scale in all_scales:
            sizes.append({'width': imageW / scale, 'height': imageH / scale })
        sizes.reverse()
        info = {
                "@id": "{0}{1}".format(cf.BASEPREF, self.identifier.value),
                "@context" : cf.context,
                "protocol" : cf.protocol,
                "width":imageW,
                "height":imageH,
                "tiles" : [{'width':cf.TILE_SIZE, 'scaleFactors': all_scales}],
                "sizes" : sizes,
                "profile": [cf.compliance,
                    {
                        "formats":["gif","tif","pdf"],
                        "supports":["regionSquare",
                                    "canonicalLinkHeader",
                                    "profileLinkHeader",
                                    "mirroring",
                                    "rotationArbitrary",
                                    "sizeAboveFull"],
                        "qualities":qualities
                    }
                ]
        }

        if cf.ATTRIBUTION:
            info['attribution'] = cf.ATTRIBUTION
        if cf.LOGO:
            info['logo'] = cf.LOGO
        if cf.LICENSE:
            info['license'] = cf.LICENSE

        if cf.AUTH_TYPE:
            info['service'] = {'@context': 'http://iiif.io/api/auth/0/context.json',
                '@id': cf.BASEPREF + cf.AUTH_URL_LOGIN,
                'profile': 'http://iiif.io/api/auth/0/login',
                'label': 'Login ({0})'.format(cf.AUTH_TYPE),
                'service': []
                }
            if cf.AUTH_URL_LOGOUT:
                info['service']['service'].append({
                '@id': cf.BASEPREF + cf.AUTH_URL_LOGOUT,
                'profile': 'http://iiif.io/api/auth/0/logout',
                'label': 'Logout ({0})'.format(cf.AUTH_TYPE)})
            if cf.AUTH_URL_TOKEN:
                info['service']['service'].append({
                '@id': cf.BASEPREF + cf.AUTH_URL_TOKEN,
                'profile': 'http://iiif.io/api/auth/0/token'})

        data = json.dumps(info, sort_keys=True)
        self.cacher.cache(self.identifier.value + "/info.json", data)
        return info

class ImageRequest(object):
    identifier = None
    region = None
    size = None
    rotation = None
    quality = None
    format = None
    image = None
    path = ""

    def __init__(self, application, path):
        self.path = path
        self.application = application
        self.image = None
        self.canonical = ""

        self.identifier = None
        self.region = None
        self.size = None
        self.rotation = None
        self.quality = None
        self.format = None

        self.param_hash = {'identifier': IdentifierParam,
            'region': RegionParam,
            'size': SizeParam,
            'rotation': RotationParam,
            'quality': QualityParam,
            'format': FormatParam}
        self.unknown = UnknownParam

    def make_param(self, which, value):
        cls = self.param_hash.get(which, self.unknown)
        inst = cls(value, self)
        setattr(self, which, inst)
        return inst

    def configure_params(self):
        for p in self.param_hash.keys():
            getattr(self, p).configure()

    def isCanonical(self):
        if not self.canonical:
            self.canonicalize()
        return self.path == self.canonical

    def canonicalize(self):
        if not self.canonical:
            params = [self.identifier, self.region, self.size, self.rotation, self.quality, self.format]
            canons = [x.canonicalize() for x in params]
            canon = "{0}/{1}/{2}/{3}/{4}.{5}".format(*canons)
            self.canonical = canon
        return self.canonical

    def make_image(self, filename):
        self.image = ImageFile(filename, self.identifier, self.application)
        return self.image

class ImageParam(object):
    value = ""
    name = ""
    valueRe = None
    app = None
    match = None

    def __init__(self, value, req):
        self.requested = value
        m = self.valueRe.match(value)
        if not m:
            raise Abort400(self.make_error_message())
        else:
            self.match = m
        self.value = value
        self.imageRequest = req

    def make_error_message(self, msg="Unable to parse"):
        return "Error processing {0} parameter value '{1}': {2} ".format(self.name, self.requested, msg)

    def canonicalize(self):
        return self.value

    def configure(self):
        pass

class IdentifierParam(ImageParam):
    valueRe = re.compile("^([^/#?@\[\]]+)$")
    name = "identifier"
    degraded = False
    value = ""
    baseValue = ""

    def __init__(self, value, req):
        value = urllib.parse.unquote(value)
        ImageParam.__init__(self, value, req)
        cf = self.imageRequest.application.config

        if value.endswith(cf.DEGRADED_IDENTIFIER):
            self.baseValue = value.replace(cf.DEGRADED_IDENTIFIER, '')
            self.degraded = True
        else:
            self.baseValue = value
        self.infoValue = urllib.parse.quote(value, '')

class RegionParam(ImageParam):
    valueRe = re.compile("^(full|square|(pct:)?([\d.]+,){3}([\d.]+))$")
    name = "region"
    x = -1
    y = -1
    width = 0
    height = 0

    def canonicalize(self):
        image = self.imageRequest.image
        if self.x == 0 and self.y == 0 and self.width == image.width and self.height == image.height:
            return "full"
        else:
            return "{0},{1},{2},{3}".format(self.x,self.y,self.width,self.height)

    def configure(self):
        image = self.imageRequest.image
        # Check region
        if self.value == 'full':
            # full size of image
            x=0;y=0;w=image.width;h=image.height
        elif self.value == 'square':
            if image.width > image.height:
                # landscape: square centered in W
                h = image.height
                w = image.height
                y = 0
                x = (image.width / 2) - (image.height / 2)
            else:
                # portrait: square centered in H
                h = image.width
                w = image.width
                x = 0
                y = (image.height / 2) - (image.height / 2)
        else:
            try:
                (x,y,w,h)=self.value.split(',')
            except:
                raise Abort400(self.make_error_message())
            if x.startswith('pct:'):
                x = x[4:]
                # convert pct into px
                try:
                    x = float(x) ; y = float(y) ; w = float(w) ; h = float(h)
                    x = int(x / 100.0 * image.width)
                    y = int(y / 100.0 * image.height)
                    w = int(w / 100.0 * image.width)
                    h = int(h / 100.0 * image.height)
                except:
                    raise Abort400(self.make_error_message())
            else:
                try:
                    x = int(x) ; y = int(y) ; w = int(w) ; h = int(h)
                except:
                    raise Abort400(self.make_error_message())

            if (x > image.width):
                raise Abort400("X coordinate is outside image")
            elif (y > image.height):
                raise Abort400("Y coordinate is outside image")
            elif w < 1:
                raise Abort400("Region width is zero")
            elif h < 1:
                raise Abort400("Region height is zero")

            if x+w > image.width:
                w = image.width-x
            if y+h > image.height:
                h = image.height-y
        self.x = x
        self.y = y
        self.width = w
        self.height = h

class SizeParam(ImageParam):
    valueRe = re.compile("^(full|[\d.]+,|,[\d.]+|pct:[\d.]+|[\d.]+,[\d.]+|![\d.]+,[\d.]+|\^[\d.]+,([\d.]+)?)$")
    name = "size"
    height = 0
    width = 0
    ratio = 0

    def canonicalize(self):
        image = self.imageRequest.image
        region = self.imageRequest.region
        if not region:
            raise NotImplementedError("Must process region before canonicalizing size")

        if (self.width == image.width and self.height == image.height):
            return "full"
        elif (self.width == region.width and self.height == region.height):
            return "full"
        elif self.ratio:
            return "{0},".format(self.width)
        else:
            return "{0},{1}".format(self.width, self.height)

    def configure(self):
        image = self.imageRequest.image
        region = self.imageRequest.region
        if not region:
            raise NotImplementedError("Must process region before configuring size")

        w = region.width
        h = region.height
        size = self.value
        # Output Size
        if size == 'full':
            sizeW = w ; sizeH = h ; ratio = 1
        else:
            try:
                if size[0] == '!':     # !w,h
                    # Must fit inside w and h
                    (maxSizeW, maxSizeH) = size[1:].split(',')
                    # calculate both ratios and pick smaller
                    if not maxSizeH:
                        maxSizeH = maxSizeW
                    ratioW = float(maxSizeW) / w
                    ratioH = float(maxSizeH) / h
                    ratio = min(ratioW, ratioH)
                    sizeW = int(w * ratio)
                    sizeH = int(h * ratio)

                elif size[-1] == ',':    # w,
                    # constrain width to w, and calculate appropriate h
                    sizeW = int(size[:-1])
                    ratio = sizeW/float(w)
                    sizeH = int(h * ratio)
                elif size[0] == ',':     # ,h
                    # constrain height to h, and calculate appropriate w
                    sizeH = int(size[1:])
                    ratio = sizeH/float(h)
                    sizeW = int(w * ratio)

                elif size.startswith('pct:'):     #pct: n
                    # n percent of size
                    ratio = float(size[4:])/100
                    sizeW = int(w * ratio)
                    sizeH = int(h * ratio)
                    if sizeW < 1:
                        sizeW = 1
                    if sizeH < 1:
                        sizeH = 1
                else:    # w,h    or invalid
                    (sw,sh) = size.split(',')
                    # exactly w and h, deforming aspect (if necessary)
                    sizeW = int(sw)
                    sizeH = int(sh)
                    # Nasty hack to get the right canonical URI
                    ratioW = sizeW/float(w)
                    tempSizeH = int(sizeH / ratioW)
                    if tempSizeH in [h, h-1, h+1]:
                        ratio = 1
                    else:
                        ratio = 0
            except:
                raise Abort400(self.make_error_message())
        self.height = sizeH
        self.width = sizeW
        self.ratio = ratio

class RotationParam(ImageParam):
    valueRe = re.compile("^(!)?([0-9.]+)$")
    name = "rotation"
    mirror = False

    def canonicalize(self):
        return "{0}{1}".format("!" if self.mirror else "", self.rotation)

    def __init__(self, value, app):
        value = value.replace("%21", '!')
        ImageParam.__init__(self, value, app)
        (mirror, rotation) = self.match.groups()
        self.mirror = mirror == "!"
        try:
            if '.' in rotation:
                rot = float(rotation)
                if rot == int(rot):
                    rot = int(rot)
            else:
                rot = int(rotation)
        except:
            raise Abort400(self.make_error_message())
        if rot < 0 or rot > 360:
            raise Abort400(self.make_error_message())
        rot = rot % 360
        self.rotation = rot

class QualityParam(ImageParam):
    valueRe = re.compile("^(default|color|gray|bitonal)$")
    name = "quality"

    def configure(self):
        quals = self.imageRequest.image.qualities
        quals.extend(["default","bitonal"])
        if not self.value in quals:
            raise Abort400(self.make_error_message("Quality not supported"))
        if self.value == quals[0]:
            self.value = "default"

class FormatParam(ImageParam):
    valueRe = re.compile("^(jpg|tif|png|gif|jp2|pdf|eps|bmp|webp)$")
    name = "format"

class UnknownParam(ImageParam):
    valueRe = re.compile("^$")
    name = "unknown"

class FileSystemResolver(object):
    identifiers = {}

    def __init__(self, app):
        self.identifiers = {}

        self.UPLOADDIR = app.config.UPLOADDIR
        self.FILEDIRS = app.config.FILEDIRS
        self.IMAGEFMTS = app.config.IMAGEFMTS

        fns = []
        for fd in self.FILEDIRS:
            for fmt in self.IMAGEFMTS:
                fns.extend(glob.glob(os.path.join(fd, "*" + fmt)))

        for fn in fns:
            (d, f) = os.path.split(fn)
            f = f[:-4]
            self.identifiers[f] = fn

    def resolve_identifier(self, identifier):
        idv = identifier.value
        if idv in self.identifiers:
            return self.identifiers[idv]
        else:
            fns = glob.glob(os.path.join(self.UPLOADDIR, idv) + '.*')
            if fns:
                self.identifiers[identifier] = fns[0]
                return fns[0]
            else:
                raise Abort404(identifier.make_error_message("Image Not Found"))

class FileSystemCacher(object):
    def __init__(self, app):
        self.application = app
        self.directory = app.config.CACHEDIR

    def cache(self, path, data):
        (dirp, filep) = os.path.split(path)
        paths = dirp.split(os.sep)

        for p in range(1,len(paths)+1):
            pth = os.path.join(self.directory, *paths[:p])
            if not os.path.exists(pth):
                os.makedirs(pth, exist_ok=True)

        if not path.startswith(self.directory):
            path = os.path.join(self.directory, path)

        fh = open(path, 'wb')
        fh.write(data)
        fh.close()

    def exists(self, path):
        if not path.startswith(self.directory):
            path = os.path.join(self.directory, path)
        return os.path.exists(path)

    def fetch(self, path):
        if not path.startswith(self.directory):
            path = os.path.join(self.directory, path)
        fh = open(path, "rb")
        data = fh.read()
        fh.close()
        return data

    def generate_media_type(self, path):
        if path.endswith("info.json"):
            # Check request headers for application/ld+json
            inacc = self.request.headers.get('Accept', '')
            if inacc.find('ld+json') > -1:
                mimetype = "application/ld+json"
            else:
                mimetype = "application/json"
        else:
            # Check in config.extensions
            dotidx = path.rfind('.')
            ext = path[dotidx+1:]
            try:
                mimetype = self.application.config.extensions[ext]
            except:
                raise Abort400("Unsupported format: {0}".format(ext))
        return mimetype

    def send_file(self, path, mt="", status=200):
        if not path.startswith(self.directory):
            path = os.path.join(self.directory, path)
        if not mt:
            mt = self.generate_media_type(path)
        fh = open(path, "rb")
        data = fh.read()
        fh.close()
        return self.application.send(data, status=status, ct=mt)

class Config(object):
    def __init__(self, info):
        for (k,v) in info.items():
            setattr(self, k, v)
        nf = []
        for f in self.FILEDIRS:
            nf.append(os.path.join(self.HOMEDIR, f))
        self.FILEDIRS = nf
        self.CACHEDIR = os.path.join(self.HOMEDIR, self.CACHEDIR)
        self.UPLOADDIR = os.path.join(self.HOMEDIR, self.UPLOADDIR)
        self.UPLOADLINKDIR = os.path.join(self.UPLOADDIR, self.UPLOADLINKDIR)
        self.BASEPREF = self.BASEURL + self.PREFIX
        self.GOOGLE_REDIRECT_URI = self.BASEPREF + self.AUTH_URL_HOME

        self.formats = {
            'BMP' : 'image/bmp',
            'GIF' : 'image/gif',
            'JPEG': 'image/jpeg',
            'PCX' : 'image/pcx',
            'PDF' :  'application/pdf',
            'PNG' : 'image/png',
            'TIFF': 'image/tiff',
            'WEBP': 'image/webp'
        }

        self.extensions = {
            'bmp' : 'image/bmp',
            'gif' : 'image/gif',
            'jpg': 'image/jpeg',
            'pcx' : 'image/pcx',
            'pdf' :  'application/pdf',
            'png' : 'image/png',
            'tif' : 'image/tiff',
            'webp': 'image/webp'
        }

        self.content_types = {}
        for (k,v) in self.extensions.items():
            self.content_types[v] = k

        self.jpegQuality = 90

        # Other possibilities:
        # cf.DEGRADED_QUALITY = "gray"
        # cf.DEGRADED_QUALITY = "bitonal"
        # cf.AUTH_TYPE = "basic"
        # cf.AUTH_TYPE = "oauth"
        # cf.CLIENT_SECRETS = {'name1':'secret1'}

class ImageHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        """
        Extra keywords:

        HOMEDIR - home for imageserver cache, etc.
        PORT -
        """
        # File path settings
        for name in ["SITE_DIR", "PORT", "HOSTNAME", "GET_IMAGE_FN"]:
            if name in kwargs:
                setattr(self, name, kwargs[name])
                del kwargs[name]
            else:
                raise Exception("ImageHandler needs '%s'" % name)
        super().__init__(*args, **kwargs)

        self.CACHEDIR = os.path.join(self.SITE_DIR, "media", "cache/")
        # FIXME, allow uploads:
        self.UPLOADDIR = os.path.join(self.SITE_DIR, "media", "upload/")
        self.UPLOADLINKDIR = os.path.join(self.SITE_DIR, "media", "upload/")
        self.MAXUPLOADFILES = 1000
        self.SUBMIT_URL = "submit"

        # URL settings
        self.BASEURL = self.HOSTNAME + ":" + str(self.PORT)
        self.PREFIX = "/imageserver"
        self.BASEPREF = self.BASEURL + self.PREFIX + '/'

        # info.json settings
        self.TILE_SIZE = 512
        self.MIN_SIZE = 50
        self.USE_LD_JSON = True
        self.ATTRIBUTION = "Provided by Example Organization"
        self.LICENSE = "http://license.example.com/license"
        self.LOGO = "http://example.com/images/logo.jpg"

        self.compliance = "http://iiif.io/api/image/2/level2.json"
        self.context = "http://iiif.io/api/image/2/context.json"
        self.protocol = "http://iiif.io/api/image"

        # Authentication settings
        self.DEGRADE_IMAGES = False
        self.DEGRADED_NOACCESS = False
        self.DEGRADED_SIZE = 400
        self.DEGRADED_QUALITY = ""
        # self.DEGRADED_QUALITY = "gray"
        # self.DEGRADED_QUALITY = "bitonal"
        # self.AUTH_TYPE = "basic"
        # self.AUTH_TYPE = "oauth"
        self.AUTH_TYPE = ""
        self.DEGRADED_IDENTIFIER = "-degraded"

        self.AUTH_URL_LOGIN = "login"
        self.AUTH_URL_LOGOUT = "logout"
        self.AUTH_URL_TOKEN = "token"
        self.AUTH_URL_HOME = "home"
        self.AUTH_URL_CLIENTCODE = "code"
        self.AUTH_URL_NOACCESS_ID = "no-access"

        #self.CLIENT_SECRETS = {}
        self.CLIENT_SECRETS = {'name1': 'secret1'}

        # Google OAuth2 settings
        self.GOOGLE_API_CLIENT_ID = 'client_id'
        self.GOOGLE_API_CLIENT_SECRET = 'client_secret'
        self.GOOGLE_REDIRECT_URI = self.BASEPREF + self.AUTH_URL_HOME
        self.GOOGLE_API_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
        self.GOOGLE_OAUTH2_URL = 'https://accounts.google.com/o/oauth2/'
        self.GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v1/'

        self.formats = {
            'BMP' : 'image/bmp',
            'GIF' : 'image/gif',
            'JPEG': 'image/jpeg',
            'PCX' : 'image/pcx',
            'PDF' :  'application/pdf',
            'PNG' : 'image/png',
            'TIFF': 'image/tiff',
            'WEBP': 'image/webp'
        }

        self.extensions = {
        'bmp' : 'image/bmp',
            'gif' : 'image/gif',
            'jpg': 'image/jpeg',
            'pcx' : 'image/pcx',
            'pdf' :  'application/pdf',
            'png' : 'image/png',
            'tif' : 'image/tiff',
            'webp': 'image/webp'
        }

        self.content_types = {}
        for (k,v) in self.extensions.items():
            self.content_types[v] = k

        self.idRe = re.compile("^([^/#?@]+)$")
        self.regionRe = re.compile("^(full|square|(pct:)?([\d.]+,){3}([\d.]+))$")
        self.sizeRe = re.compile("^(full|[\d.]+,|,[\d.]+|pct:[\d.]+|[\d.]+,[\d.]+|![\d.]+,[\d.]+|\^[\d.]+,([\d.]+)?)$")
        self.rotationRe = re.compile("^(!)?([0-9.]+)$")
        self.qualityRe = re.compile("^(default|color|gray|bitonal)$")
        self.formatRe = re.compile("^(jpg|tif|png|gif|jp2|pdf|eps|bmp|webp)$")
        self.infoRe = re.compile("/([^/#?@]+)/info.json$")
        self.badcharRe= re.compile('[\[\]?@#/]')

        # encoding param for PIL
        self.jpegQuality = 90
        self.identifiers = {}

    def send_file(self, filename, mt, status=200):
        if not filename.startswith(self.CACHEDIR):
            filename = os.path.join(self.CACHEDIR, filename)
        fh = open(filename, "rb")
        data = fh.read()
        fh.close()
        return self.send(data, status=status, ct=mt)

    def send(self, data, status=200, ct="text/plain"):
        self.set_header("Content-Type", ct)
        self.set_status(status)
        self.write(data)

    def error(self, status, message=""):
        self.status = status
        self.set_header("Content-Type", 'text/plain')
        if message:
            return message
        else:
            return self.codes[status]

    def error_msg(self, param, msg, status):
        text = "An error occured when processing the '{0}' parameter: {1}".format(param, msg)
        self.set_status(status, text)
        self.finish(text)

    def get_image_file(self, identifier):
        """
        Given an image identifier, return the full path/filename.
        Side-effect: cache the identifier -> path/filename.
        """
        path = ""
        if identifier in self.identifiers:
            path = self.identifiers[identifier]
        elif self.GET_IMAGE_FN:
            path = self.GET_IMAGE_FN(identifier)
        else:
            path = self.get_image_file_from_filesystem(identifier)
        # cache it:
        if path:
            self.identifiers[identifier] = path
        return path

    def get_image_file_from_filesystem(self, identifier):
        """
        Given an image identifier in UPLOADDIR, return the full path/filename.
        """
        fns = glob.glob(os.path.join(self.UPLOADDIR, identifier) + '.*')
        if fns:
            return fns[0]
        else:
            return ""

    def make_info(self, infoId, image):
        (imageW, imageH) = image.size

        if self.DEGRADE_IMAGES and infoId.endswith(self.DEGRADED_IDENTIFIER) and self.DEGRADED_SIZE:
            # Make max 400 on long edge and add in auth service
            if imageW > imageH:
                ratio = float(self.DEGRADED_SIZE) / imageW
                imageH = int(imageH * ratio)
                imageW = self.DEGRADED_SIZE
            else:
                ratio = float(self.DEGRADED_SIZE) / imageH
                imageW = int(imageW * ratio)
                imageH = self.DEGRADED_SIZE

        all_scales = []
        sfn = 0
        sf = 1
        while float(imageH)/sf > self.MIN_SIZE and float(imageW)/sf > self.MIN_SIZE:
            all_scales.append(sf)
            sfn += 1
            sf = 2**sfn

        if image.mode == '' or (self.DEGRADE_IMAGES and self.DEGRADED_QUALITY == 'bitonal'):
            qualities = []
        elif image.mode == 'L' or (self.DEGRADE_IMAGES and self.DEGRADED_QUALITY == 'gray'):
            qualities = ['gray']
        else:
            qualities = ['color','gray']

        sizes = []
        for scale in all_scales:
            sizes.append({'width': imageW / scale, 'height': imageH / scale })
        sizes.reverse()
        info = {
                "@id": "{0}{1}".format(self.BASEPREF, infoId),
                "@context" : self.context,
                "protocol" : self.protocol,
                "width":imageW,
                "height":imageH,
                "tiles" : [{'width':self.TILE_SIZE, 'scaleFactors': all_scales}],
                "sizes" : sizes,
                "profile": [self.compliance,
                    {
                        "formats":["gif","tif","pdf"],
                        "supports":["regionSquare",
                                    "canonicalLinkHeader",
                                    "profileLinkHeader",
                                    "mirroring",
                                    "rotationArbitrary",
                                    "sizeAboveFull"],
                        "qualities":qualities
                    }
                ]
        }
        if qualities:
            info["profile"][1]["qualities"] = qualities

        if self.ATTRIBUTION:
            info['attribution'] = self.ATTRIBUTION
        if self.LOGO:
            info['logo'] = self.LOGO
        if self.LICENSE:
            info['license'] = self.LICENSE

        if self.AUTH_TYPE:
            info['service'] = {'@context': 'http://iiif.io/api/auth/0/context.json',
                '@id': self.BASEPREF + self.AUTH_URL_LOGIN,
                'profile': 'http://iiif.io/api/auth/0/login',
                'label': 'Login ({0})'.format(self.AUTH_TYPE),
                'service': []
                }
            if self.AUTH_URL_LOGOUT:
                info['service']['service'].append({
                '@id': self.BASEPREF + self.AUTH_URL_LOGOUT,
                'profile': 'http://iiif.io/api/auth/0/logout',
                'label': 'Logout ({0})'.format(self.AUTH_TYPE)})
            if self.AUTH_URL_TOKEN:
                info['service']['service'].append({
                '@id': self.BASEPREF + self.AUTH_URL_TOKEN,
                'profile': 'http://iiif.io/api/auth/0/token'})

        data = json.dumps(info, sort_keys=True)

        try:
            os.makedirs(os.path.join(self.CACHEDIR,infoId), exist_ok=True)
        except OSError:
            # directory already exists
            pass
        fh = open(os.path.join(self.CACHEDIR, infoId, 'info.json'), 'w')
        fh.write(data)
        fh.close()
        return info

    def watermark(self, image):
        # Do watermarking here
        return image

    @tornado.web.authenticated
    def get(self, path):
        """
        Path is an IIIF image server set of parameters:

        /identifier/region/scale/format.type

        Example:

          identifier - filename or handle
          region - full, or x1,y1,x2,y2
          scale - width, or width,height
          format - default, ...
          type - jpg, gif, or tiff

        """
        # First check auth
        #if self.DEGRADE_IMAGES:
        #    isAuthed = request.get_cookie(self.COOKIE_NAME, secret=self.COOKIE_SECRET)
        #    authToken = request.headers.get('Authorization', '')
        #    hasToken = len(authToken) > 0
        #else:
        isAuthed = True
        hasToken = True
        degraded = False

        # http://{server}{/prefix}   /{identifier}/{region}/{size}/{rotation}/{quality}{.format}
        bits = path.split('/')

        ## self.set_header('Access-Control-Allow-Origin', '*')

        # Nasty but useful debugging hack
        if len(bits) == 1 and bits[0] == "list":
            return self.send(repr(self.identifiers), status=200, ct="application/json");

        if bits:
            identifier = bits.pop(0)
            if identifier.endswith(self.DEGRADED_IDENTIFIER):
                undegraded = identifier.replace(self.DEGRADED_IDENTIFIER, '')
                degraded = True
            else:
                undegraded = identifier

            if self.idRe.match(identifier) == None:
                return self.error_msg("identifier", "Identifier invalid: {0}".format(identifier), status=400)
            else:
                # Check []?#@ (will never find / )
                if self.badcharRe.match(identifier):
                    return self.error_msg('identifier', 'Unescaped Characters', status=400)
                identifier = urllib.parse.unquote(identifier)
                infoId = urllib.parse.quote(identifier, '')
                filename = self.get_image_file(undegraded)
                if not filename:
                    return self.error_msg('identifier', 'Not found: {0}'.format(identifier), status=404)
        else:
            return self.error_msg("identifier", "Identifier unspecified", status=400)

        self.set_header("Link", '<{0}>;rel="profile"'.format(self.compliance))

        # Early cache check here
        fp = path
        if fp == identifier or fp == "{0}/".format(identifier):
            self.set_status(303)
            self.set_header("Link", "{0}{1}/info.json".format(self.BASEPREF, infoId))
            return
        elif len(fp) > 9 and fp[-9:] == "info.json":
            # Check request headers for application/ld+json
            inacc = self.request.headers.get('Accept', '')
            if inacc.find('ld+json') > -1:
                mimetype = "application/ld+json"
            else:
                mimetype = "application/json"
        elif len(fp) > 4 and fp[-4] == '.':
            try:
                mimetype = self.extensions[fp[-3:]]
            except:
                # no such format, early break
                return self.error_msg('format', 'Unsupported format', status=400)

        if identifier.find(self.DEGRADED_IDENTIFIER) == -1:
            if mimetype.endswith('json'):
                if not hasToken:
                    if self.DEGRADED_NOACCESS:
                        # No access is special degraded
                        return self.send_file(fp, mimetype, status=401)

                        # self.error_msg('auth', 'auth test', status=401)
                        # redirect('%sno-access/info.json' % BASEPREF)
                    else:
                        # Or restrict size to max edge of 400 as degradation
                        redirect('{0}{1}{2}/info.json'.format(self.BASEPREF, identifier, self.DEGRADED_IDENTIFIER))
            elif not isAuthed:
                # Block access to images
                return self.error_msg('auth', 'Not authenticated', status=401)

        if os.path.exists(self.CACHEDIR + fp):
            # Will only ever be canonical, otherwise would redirect
            self.set_header('Link',
                            self.request.headers.get("Link", "") +
                            ', <{0}{1}>;rel="canonical"'.format(self.BASEPREF, fp))
            return self.send_file(fp, mimetype)

        if bits:
            region = bits.pop(0)
            if self.regionRe.match(region) == None:
                # test for info.json
                if region == "info.json":
                    # build and return info
                    inacc = self.request.headers.get('Accept', '')
                    if inacc.find('ld+json') > -1:
                        mt = "application/ld+json"
                    else:
                        mt = "application/json"
                    if not os.path.exists(infoId +'/'+region):
                        image = Image.open(filename)
                        self.make_info(infoId, image)
                        try:
                            image.close()
                        except:
                            pass
                    return self.send_file(infoId +'/' + region, mt)
                else:
                    return self.error_msg("region", "Region invalid: {0}".format(region), status = 400)
        # else is caught by checking identifier in early cache check

        if bits:
            size = bits.pop(0)
            if self.sizeRe.match(size) == None:
                return self.error_msg("size", "Size invalid: {0}".format(size), status = 400)
        else:
            return self.error_msg("size", "Size unspecified", status=400)

        if bits:
            rotation = bits.pop(0)
            rotation = rotation.replace("%21", '!')
            m = self.rotationRe.match(rotation)
            if m == None:
                return self.error_msg("rotation", "Rotation invalid: {0}".format(rotation), status = 400)
            else:
                mirror, rotation = m.groups()
        else:
            return self.error_msg("rotation", "Rotation unspecified", status=400)

        if bits:
            quality = bits.pop(0)
            dotidx = quality.rfind('.')
            if dotidx > -1:
                format = quality[dotidx+1:]
                quality = quality[:dotidx]
            else:
                return self.error_msg("format", "Format not specified but mandatory", status=400)
            if self.qualityRe.match(quality) == None:
                return self.error_msg("quality", "Quality invalid: {0}".format(quality), status = 400)
            elif self.formatRe.match(format) == None:
                return self.error_msg("format", "Format invalid: {0}".format(format), status = 400)
        else:
            return self.error_msg("quality", "Quality unspecified", status=400)

        # MUCH quicker to load JSON than the image to find h/w
        # Does json already exist?
        if os.path.exists(self.CACHEDIR+infoId):
            # load JSON info file or image?
            fh = open(os.path.join(self.CACHEDIR, infoId, 'info.json'))
            info = json.load(fh)
            fh.close()
            image = None
        else:
            # Need to load it up for the first time!
            if os.path.exists(filename):
                image = Image.open(filename)
                info = self.make_info(infoId, image)
                imageW = info['width']
                imageH = info['height']
            else:
                image = None
        if image is None:
            self.set_status(404, "File does not exist.")
            self.finish("File does not exist.")
            return

        # Check region
        if region == 'full':
            # full size of image
            x=0;y=0;w=imageW;h=imageH
        elif region == 'square':
            if imageW > imageH:
                # landscape: square centered in W
                h = imageH
                w = imageH
                y = 0
                x = (imageW / 2) - (imageH / 2)
            else:
                # portrait: square centered in H
                h = imageW
                w = imageW
                x = 0
                y = (imageH / 2) - (imageW / 2)
        else:
            try:
                (x,y,w,h)=region.split(',')
            except:
                return self.error_msg('region',
                    'unable to parse region: {0}'.format(region), status=400)
            if x.startswith('pct:'):
                x = x[4:]
                # convert pct into px
                try:
                    x = float(x) ; y = float(y) ; w = float(w) ; h = float(h)
                    x = int(x / 100.0 * imageW)
                    y = int(y / 100.0 * imageH)
                    w = int(w / 100.0 * imageW)
                    h = int(h / 100.0 * imageH)
                except:
                    return self.error_msg('region', 'unable to parse region: {0}'.format(region), status=400)
            else:
                try:
                    x = int(x) ; y = int(y) ; w = int(w) ; h = int(h)
                except:
                    return self.error_msg('region', 'unable to parse region: {0}'.format(region), status=400)

            if (x > imageW):
                return self.error_msg("region", "X coordinate is outside image", status=400)
            elif (y > imageH):
                return self.error_msg("region", "Y coordinate is outside image", status=400)
            elif w < 1:
                return self.error_msg("region", "Region width is zero", status=400)
            elif h < 1:
                return self.error_msg("region", "Region height is zero", status=400)

            # PIL will create whitespace outside, so constrain
            # Need this info for next step anyway
            if x+w > imageW:
                w = imageW-x
            if y+h > imageH:
                h = imageH-y

        # Output Size
        if size == 'full':
            sizeW = w ; sizeH = h
        else:
            try:
                if size[0] == '!':     # !w,h
                    # Must fit inside w and h
                    (maxSizeW, maxSizeH) = size[1:].split(',')
                    # calculate both ratios and pick smaller
                    if not maxSizeH:
                        maxSizeH = maxSizeW
                    ratioW = float(maxSizeW) / w
                    ratioH = float(maxSizeH) / h
                    ratio = min(ratioW, ratioH)
                    sizeW = int(w * ratio)
                    sizeH = int(h * ratio)

                elif size[-1] == ',':    # w,
                    # constrain width to w, and calculate appropriate h
                    sizeW = int(size[:-1])
                    ratio = sizeW/float(w)
                    sizeH = int(h * ratio)
                elif size[0] == ',':     # ,h
                    # constrain height to h, and calculate appropriate w
                    sizeH = int(size[1:])
                    ratio = sizeH/float(h)
                    sizeW = int(w * ratio)

                elif size.startswith('pct:'):     #pct: n
                    # n percent of size
                    ratio = float(size[4:])/100
                    sizeW = int(w * ratio)
                    sizeH = int(h * ratio)
                    if sizeW < 1:
                        sizeW = 1
                    if sizeH < 1:
                        sizeH = 1
                else:    # w,h    or invalid
                    (sw,sh) = size.split(',')
                    # exactly w and h, deforming aspect (if necessary)
                    sizeW = int(sw)
                    sizeH = int(sh)
                    # Nasty hack to get the right canonical URI
                    ratioW = sizeW/float(w)
                    tempSizeH = int(sizeH / ratioW)
                    if tempSizeH in [h, h-1, h+1]:
                        ratio = 1
                    else:
                        ratio = 0
            except:
                return self.error_msg('size', 'Size unparseable: {0}'.format(size), status=400)

        # Process rotation
        try:
            if '.' in rotation:
                rot = float(rotation)
                if rot == int(rot):
                    rot = int(rot)
            else:
                rot = int(rotation)
        except:
            return self.error_msg('rotation', 'Rotation unparseable: {0}'.format(rotation), status=400)
        if rot < 0 or rot > 360:
            return self.error_msg('rotation', 'Rotation must be 0-359.99: {0}'.format(rotation), status=400)
        # 360 --> 0
        rot = rot % 360

        quals = info['profile'][1]['qualities']
        quals.extend(["default","bitonal"])
        if not quality in quals:
            return self.error_msg('quality', 'Quality not supported for this image: {0} not in {1}'.format(quality, quals), status=501)
        if quality == quals[0]:
            quality = "default"

        nformat = format.upper()
        if nformat == 'JPG':
            nformat = 'JPEG'
        elif nformat == "TIF":
            nformat = "TIFF"
        try:
            mimetype = self.formats[nformat]
        except:
            return self.error_msg('format', 'Unsupported format', status=415)

        # Check if URI is not canonical, if so redirect to canonical URI
        # Check disk cache and maybe redirect
        if x == 0 and y == 0 and w == imageW and h == imageH:
            c_region = "full"
        else:
            c_region = "{0},{1},{2},{3}".format(x,y,w,h)

        if (sizeW == imageW and sizeH == imageH) or (w == sizeW and h == sizeH):
            c_size = "full"
        elif ratio:
            c_size = "{0},".format(sizeW)
        else:
            c_size = "{0},{1}".format(sizeW, sizeH)

        c_rot = "!{0}".format(rot) if mirror else str(rot)
        c_qual = "{0}.{1}".format(quality, format.lower())
        paths = [infoId, c_region, c_size, c_rot, c_qual]
        fn = os.path.join(*paths)
        new_url = self.BASEPREF + fn
        #self.set_header('Link',
        #                self.request.headers.get("Link", "") +
        #                ', <{0}>;rel="canonical"'.format(new_url))
        if fn != path:
            #self.set_header('Location', new_url)
            #return self.send("", status=301)
            self.redirect("/imageserver/" + fn)
            return

        # Won't regenerate needlessly as earlier cache check would have found it
        # if we're canonical already

        # And finally, process the image!
        if image == None:
            try:
                image = Image.open(filename)
            except IOError:
                return self.error_msg('identifier', 'Unsupported format for base image', status=501)

        if identifier.endswith(self.DEGRADED_IDENTIFIER):
            if self.DEGRADED_SIZE > 0:
                # resize max size
                image = image.resize((info['width'], info['height']))
            if self.DEGRADED_QUALITY:
                nquality = {'gray':'L','bitonal':'1'}[self.DEGRADED_QUALITY]
                image = image.convert(nquality)

        if (w != info['width'] or h != info['height']):
            box = (x,y,x+w,y+h)
            image = image.crop(box)

        if sizeW != w or sizeH != h:
            image = image.resize((sizeW, sizeH))
        if mirror:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if rot != 0:
            # NB Rotation in PIL can introduce extra pixels on edges, even for square
            # PIL is counter-clockwise, so need to reverse
            rot = 360 - rot
            try:
                image = image.rotate(rot, expand=1)
            except:
                # old version of PIL without expand
                segx = image.size[0]
                segy = image.size[1]
                angle = radians(rot)
                rx = abs(segx * cos(angle)) + abs(segy * sin(angle))
                ry = abs(segy * cos(angle)) + abs(segx * sin(angle))

                bg = Image.new("RGB", (rx, ry), (0, 0, 0))
                tx = int((rx - segx)/2)
                ty = int((ry - segy)/2)
                bg.paste(image, (tx ,ty, tx + segx, ty + segy))
                image = bg.rotate(rot)

        if quality != 'default':
            nquality = {'color':'RGB','gray':'L','bitonal':'1'}[quality]
            image = image.convert(nquality)

        # Can't save alpha mode in jpeg
        if nformat == 'JPEG' and image.mode == 'P':
            image = image.convert('RGB')

        output = io.BytesIO()
        try:
            image.save(output,format=nformat, quality=self.jpegQuality)
        except SystemError:
            return self.error_msg('size', 'Unsupported size... tile cannot extend outside image', status=501)
        except IOError:
            return self.error_msg('format', 'Unsupported format for format', status=501)
        contents = output.getvalue()
        output.close()

        # Write to disk cache
        for p in range(1,len(paths)):
            pth = os.path.join(self.CACHEDIR, *paths[:p])
            if not os.path.exists(pth):
                os.makedirs(pth, exist_ok=True)
        fh = open(self.CACHEDIR + fn, 'wb')
        fh.write(contents)
        fh.close()

        return self.send(contents, ct=mimetype)

    def noaccess(self):
        noacc = {"@context": "http://iiif.io/api/image/2/context.json",
                 "@id": self.BASEPREF + "no-access",
                 "protocol": "http://iiif.io/api/image",
                 "height": 1,
                 "width": 1,
                 "service": {"@context": "http://iiif.io/api/auth/1/context.json",
                             "@id": self.BASEPREF + "login",
                             "profile": "iiif:auth-service"}}
        self.set_header('Access-Control-Allow-Origin', '*')
        return self.send(json.dumps(noacc), ct="application/json")

    def get_client_code(self):
        # will be POSTED:
        # {'clientId': x, 'clientSecret': y}
        if not self.CLIENT_SECRETS:
            raise Abort404("invalid request")

        bod = self.request.body
        js = json.loads(bod)
        name = js['clientId']
        secret = js['clientSecret']
        if self.CLIENT_SECRETS.get(name, '') == secret:
            data = {'authorizationCode' : code}
        else:
            data = {'error': 'invalidClientSecret'}
        dataStr = json.dumps(dataStr)
        return self.send(dataStr, ct="application/json")

    def handle_submit(self):
        imgurl = self.get_query_argument('url', '')
        if not imgurl:
            # Need a url
            raise Abort400("Missing required parameter: url")

        # cache check
        md = hashlib.md5(imgurl)
        imgid = md.hexdigest()
        done = glob.glob("{0}*".format(os.path.join(self.UPLOADDIR, imgid)))
        if not done:
            # fetch URL
            fh = urllib.parse.urlopen(imgurl)
            ct = fh.headers['Content-Type']
            if ct.find('image/') == -1:
                # Not an image!
                raise Abort400("That resource is not an image")
            data = fh.read()
            fh.close()

            # store the url / hash somewhere
            fn = os.path.join(self.UPLOADLINKDIR, "{0}.url.txt".format(imgid))
            fh = open(fn, 'w')
            fh.write(imgurl)
            fh.close()

            ext = self.content_types.get(ct, 'jpg')
            filename = "{0}.{1}".format(imgid, ext)
            fn = os.path.join(self.UPLOADDIR, filename)
            fh = open(fn, 'wb')
            fh.write(data)
            fh.close()

            files = os.listdir(self.UPLOADDIR)
            if len(files) > self.MAXUPLOADFILES:
                # trash oldest one
                mtime = lambda f: os.stat(os.path.join(self.UPLOADDIR, f)).st_mtime
                ofiles = list(sorted(files, key=mtime))
                os.remove(os.path.join(self.UPLOADDIR, ofiles[0]))

        link = self.BASEPREF + imgid
        redirect(link + '/info.json')
