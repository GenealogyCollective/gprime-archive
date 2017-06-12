# gPrime

[![Build Status](https://travis-ci.org/GenealogyCollective/gprime.svg?branch=master)](https://travis-ci.org/GenealogyCollective/gprime) [![codecov](https://codecov.io/gh/GenealogyCollective/gprime/branch/master/graph/badge.svg)](https://codecov.io/gh/GenealogyCollective/gprime)

gPrime is a web-based application for genealogy. It uses the Gramps API for data, reports, import/export, etc.

* Designed for collaboration and fast processing of large databases
* Multi-user, password protected
* Supports IIIF Image Server API - http://iiif.io/api/image/2.1/
* Uses a powerful search interface
* 100% compatible with [Gramps](https://gramps-project.org) data model

Additional Information
----------------------

* Blog - https://genealogycollective.wordpress.com/
* Mailing list - https://groups.google.com/forum/#!forum/genealogycollective
* Documentation - https://github.com/GenealogyCollective/gprime/tree/master/docs#gprime-documentation
* Demo - http://demo.gprime.info (username: demo, password: demo)

Get Involved!
-------------

gPrime is looking for help on many different topics:

* programming - in Python and Javascript
* translation into other languages - see demo for what exists
* CSS and HTML design - gPrime uses both

gPrime is also looking for some advsiors! If you would like to help developed focused goals for the future development of gPrime, please let us know:

[I'm interested in Advising gPrime](https://docs.google.com/forms/d/e/1FAIpQLSfhxC0mnVtweau0snweFW5-2Td8I9Wj-sCXpokeVT7EBLAypw/viewform)

Requirements
------------

* Python3

Python package dependencies:

* tornado
* PIL
* simplejson
* passlib
* meta

Installation
-------------

On Windows and Mac, perhaps the easiest method of using gPrime is to start with an [Anaconda Python3 environment](https://www.continuum.io/downloads).

Once you have a Python environment, install gPrime with:

```
pip install gprime --user -U
```

(--user installs into user space, not global space. -U updates gPrime and dependencies. Leave off --user and use Adminstrative install method (sudo) to install for everyone.)


Getting Started
---------------

To run gPrime, you need to do two things:

1. Create a site directory
2. Create at least one user and password

To create a site directory, provide a name for the tree:

```
gprime --create="My Family Tree"
```

Then, you need at least one user (as an example, we use "demo" as the username):

```
gprime --add-user --user=demo
Password: (does not show any characters as you type)
```

Importing Data
--------------

Optionally, you may now want to also import some data (gPrime supports Gramps XML, GEDCOM, and JSON import formats):

```
gprime --import-file="FamilyTree.gramps"
```

The site-directory has a folder named "media" for all of the images and other documents. On --file-import, gPrime will atempt to import any identified media by copying them into this media folder. If you want to prevent the copying, use --import-media=False. You can alternatively manually copy files into the media folder, or, in the previous example, make family_tree/media link to your media folder.

Running
-------

You can run gprime directly from either the github-downloaded directory, or from the installed version.

Installed version:

```
gprime
```

Options:
------------

* --create=TREE-NAME - Create a site directory (given by --site-dir) and family tree database with TREE-NAME
* --add-user --user=USERNAME - Add a username and password; prompts for password if --password not given
* --password=PASSWORD - Use with --change-password, or --add-user (this option is not recommended)
* --permissions=PERMS - Use `add`, `edit`, and/or `delete` separated by commas
* --change-password --user=USERNAME - Change a user's password; prompts for password if --password not given
* --site-dir=/PATH/TO/FOLDER - The directory of the gPrime site directory
* --sitename="Site Name" - Name to use for the site (optional, "gPrime" is default)
* --remove-user=USERNAME - Remove a user's username and password from "SITE-DIR/passwd" file
* --import-file=FILENAME - Import a Gramps-supported file type (.ged, .gramps, .json, etc.)
* --import-media=True/False - Attempt to import media with Gramps XML or JSON, used with --import-file
* --info - Show information about users (language, css, permissions, etc.)
* --config-file=FILE - A config file of these options (optional); alternatively, will use SITE-DIR/config.cfg if one
* --port=PORT-NUMBER - Port to listen on (8000 is default)
* --hostname=LOCALHOST - Hostname to listen on ("localhost" is default)
* --prefix=/PATH - a URL prefix (e.g., /PATH/person/ )
* --server=True|False - Start the server? Default is True
* --open-browser=True|False - open a web browser on startup?
* --debug=True|False - Use to see additional debugging information; useful for development (auto-restarts server on code change)
* --xsrf=True/False - Use cross-site request forgery protection (recommended)
* --help - List additional options and details

Rather than having to list all of these options on a command-line, you can put them in the SITE-DIR/config.cfg file:

```
### This is the contents of file SITE-DIR/config.cfg.
### Note that hyphens in option names are converted to underscores.

port     = 8001
site_dir = "My_Family_Tree_Folder"
prefix   = "/jones"
sitename = "Jerry's"
```

Common variations
-----------------

```
gprime --help
gprime --create="Smith Family"
gprime --import-file="myinfo.gramps"
gprime --add-user --user=demo --password=demo
gprime --add-user --user=demo --password=demo --permissions=add,edit
gprime --add-user --user=demo --password=demo --permissions=none
gprime
```
