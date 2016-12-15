# gPrime

[![Build Status](https://travis-ci.org/GenealogyCollective/gprime.svg?branch=master)](https://travis-ci.org/GenealogyCollective/gprime) [![codecov](https://codecov.io/gh/GenealogyCollective/gprime/branch/master/graph/badge.svg)](https://codecov.io/gh/GenealogyCollective/gprime)

gPrime is a web-based application for genealogy. It uses the Gramps API for data, reports, import/export, etc.

* Designed for collaboration and large databases
* Multi-user, password protected
* Support IIIF Image Server API - http://iiif.io/api/image/2.1/

Requirements
------------

* Python3

Python packages:

* tornado
* PIL
* simplejson
* passlib

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

Running
-------

You can run gprime directly from either the downloaded directory, or from the installed version.

Installed version:

```
python3 -m gprime.app --config="familytree.conf"
```

Downloaded versions:

```
export PYTHONPATH=/path/to/gprime
python3 -m gprime.app --config="familytree.cfg"
```

Where `familytree.cfg` contains options and values, such as:

```
port     = 8000
site_dir = "My Family Tree"
username = "demo"
```
or 

```
site_dir      = "/home/dblank/Desktop/Blank_Family/Blank Family/"
username      = "demo"
password_hash = "$5$rounds=535000$cFxCHFY.x1Ks3owt$PJYZtnr.LMDyRQXjLw8JWenNnNjKSWjRUjYJaPW4bn2"
language      = "fr"
```

If you do not provide `--password-hash` (an encrypt password) on the command-line or in the config file then a plaintext password will be interactively requested, and the crypt generated.

Options:
------------

* --site-dir=PATH - The directory of the gPrime site directory (required)
* --username=USERNAME - Username (required)
* --sitename="Site Name" - Name to use for the site (gPrime is default)
* --password-hash=HASH - Password hash for username
* --create=TREE-NAME - Create a site directory (given by --site-dir) and family tree database with TREE-NAME
* --import-file=FILENAME - Import a Gramps-supported file type (.ged, .gramps, .json, etc.)
* --language=LANG_CODE - Language code (eg, "fr") for language to show webpages
* --port=PORT-NUMBER - Port to use (8000 is default)
* --hostname=LOCALHOST - Hostname to use (localhost is default)
* --server=True|False - Start the server? Default is True
* --open-browser=True|False - open a web browser on startup?
* --debug=True|False - Use to see additional debugging information
* --xsrf=True/False - Use cross-site request forgery protection

Common variations
-----------------

```
python3 -m gprime.app --create="Smith Family" --site-dir="gprime_folder" --username=demo --server=False

python3 -m gprime.app --site-dir="gprime_folder" --import-file="myinfo.gramps" --username=demo --server=False

python3 -m gprime.app --site-dir="/path/to/gprime_folder" --username=demo

python3 -m gprime.app --help
```
