# gPrime

gPrime is a web-based application for genealogy. It uses the Gramps API for data, reports, import/export, etc.

* Designed for collaboration and large databases
* Multi-user, password protected
* Support IIIF Image Server API - http://iiif.io/api/image/2.1/

Requirements
------------

* Python3
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
port = 8000
database = "My Family Tree"
username = "demo"
```
or 

```
database      = "/home/dblank/Desktop/Blank_Family/Blank Family/"
username      = "demo"
password_hash = "$5$rounds=535000$cFxCHFY.x1Ks3owt$PJYZtnr.LMDyRQXjLw8JWenNnNjKSWjRUjYJaPW4bn2"
language      = "fr"
```

If you do not provide `--password-hash` (an encrypt password) on the command-line or in the config file then a plaintext password will be interactively requested, and the crypt generated.

Options:
------------

* --create - Create a directory and family tree
* --import-file - Import a Gramps-supported file type (.ged, .gramps, .json, etc.)
* --database - The directory or name of the Family Tree database
* --username - Username 
* --password-hash - Password hash for username
* --language - Language code (eg, "fr") for language to show webpages
* --debug - Use to see additional debugging information
* --port - Port to use (8000 is default)
* --hostname - Hostname to use (localhost is default)
* --sitename - Name to use for the site (gPrime is default)
* --data_dir - Folder of data (templates)
* --home_dir - Home directory
* --server - Start the server? Default is True
* --xsrf - Use cross-site request forgery protection

Common variations
-----------------

```
python3 -m gprime.app --create="Smith Family" --username=demo --server=False

python3 -m gprime.app --database="Smith Family" --import-file="myinfo.gramps" --username=demo --server=False

python3 -m gprime.app --database="Smith Family" --username=demo

python3 -m gprime.app --help
```
