# gPrime

[![Build Status](https://travis-ci.org/GenealogyCollective/gprime.svg?branch=master)](https://travis-ci.org/GenealogyCollective/gprime) [![codecov](https://codecov.io/gh/GenealogyCollective/gprime/branch/master/graph/badge.svg)](https://codecov.io/gh/GenealogyCollective/gprime)

gPrime is a web-based application for genealogy. It uses the Gramps API for data, reports, import/export, etc.

* Designed for collaboration and large databases
* Multi-user, password protected
* Support IIIF Image Server API - http://iiif.io/api/image/2.1/

Additional Information
----------------------

* Blog - https://genealogycollective.wordpress.com/
* Mailing list - https://groups.google.com/forum/#!forum/genealogycollective

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

Install from github:

```
git clone --depth 1 https://github.com/GenealogyCollective/gprime
cd gprime
```
Once you have the source files, you can:

```
python3 setup.py build
python3 setup.py install
```

or simply:

```
pip install . --user -U
```

Released version installation (once released):

```
pip3 install gprime
```

Getting Started
---------------

To run gPrime, you need to do two things:

1. Create a site directory
2. Create at least one user and password

To create a site directory, provide a name for the tree, and give the site-dir directory:

```
python3 -m gprime.app --create="My Family Tree" --site-dir="family_tree"
```

Then, you need at least one user (as an example, we use "demo" as the username):

```
python3 -m gprime.app --site-dir="~/family_tree" --add-user=demo
Password: (does not show any characters)
```

Optionally, you may now want to also import some data (see below). The site-directory has a folder named "media" for all of the images and other documents. You can copy them here, or, in the previous example, make ~/family_tree/media link to your media folder.

Running
-------

You can run gprime directly from either the downloaded directory, or from the installed version.

Installed version:

```
python3 -m gprime.app --config-file="familytree.conf"
```

Downloaded versions:

```
export PYTHONPATH=/path/to/gprime
python3 -m gprime.app --config-file="familytree.cfg"
```

Where `familytree.cfg` contains options and values, such as:

```
port     = 8001
site_dir = "My_Family_Tree_Folder"
```
or

```
site_dir      = "/home/dblank/Desktop/Blank_Family/Blank Family/"
language      = "fr"
```

Options:
------------

* --site-dir=PATH - The directory of the gPrime site directory (required)
* --config-file=FILE - A config file of these options (optional)
* --sitename="Site Name" - Name to use for the site (optional, "gPrime" is default)
* --language=LANG_CODE - Language code (eg, "fr") for language to show webpages ("en", English, is default)
* --create=TREE-NAME - Create a site directory (given by --site-dir) and family tree database with TREE-NAME
* --add-user=USERNAME - Add a username and password; prompts for password if --password not given
* --remove-user=USERNAME - Remove a user's username and password from "SITE-DIR/passwd" file
* --change-password=USERNAME - Change a user's password; prompts for password if --password not given
* --password=PASSWORD - Use with --change-password, or --add-user (this option is not recommended)
* --import-file=FILENAME - Import a Gramps-supported file type (.ged, .gramps, .json, etc.)
* --port=PORT-NUMBER - Port to listen on (8000 is default)
* --hostname=LOCALHOST - Hostname to listen on ("localhost" is default)
* --server=True|False - Start the server? Default is True
* --open-browser=True|False - open a web browser on startup?
* --debug=True|False - Use to see additional debugging information; useful for development (auto-restarts server)
* --xsrf=True/False - Use cross-site request forgery protection (recommended)
* --help - List additional options and details

Common variations
-----------------

```
python3 -m gprime.app --create="Smith Family" --site-dir="gprime_folder"

python3 -m gprime.app --site-dir="gprime_folder" --import-file="myinfo.gramps"

python3 -m gprime.app --site-dir="/path/to/gprime_folder"

python3 -m gprime.app --help
```
