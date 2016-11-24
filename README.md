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

Installation
-------------

Install from github:

```shell
git clone --depth 1 https://github.com/GenealogyCollective/gprime
cd gprime
python3 setup.py build
sudo python3 setup.py install
```

Released version installation (once released):

```shell
pip3 install gprime
```

Running
-------

You can run gprime directly from either the downloaded directory, or from the installed version.

Installed version:

```shell
python3 -m gprime.app --config="familytree.conf"
```
Downloaded versions:

```shell
export PYTHONPATH=/path/to/gprime
python3 -m gprime.app --config="familytree.conf"
```

Where `familytree.conf` contains options and values, such as:

```python
port = 8000
database = "My Family Tree"
username = "demo"
```

If you do not provide `--password` (a crypt-based password) on the command-line or in the config file then a plaintext password will be interactively requested, and the crypt generated.

Options:
------------

* --create - Create a directory and family tree
* --import-file - Import a Gramps-supported file type (.ged, .gramps, .json, etc.)
* --database - The directory or name of the database
* --username - Username (demo)
* --password - Password (demo)
* --debug - Use to see additional debugging information
* --port - Port to use (8000 is default)
* --hostname - Hostname to use (localhost is default)
* --sitename - Name to use for the site (gPrime is default)
* --data_dir - Folder of gprime/data
* --home_dir - Gramps home
* --server - Start the server? Default is True
* --xsrf - Use cross-site request forgery protection

Common variations
-----------------

```shell
python3 -m gprime.app --create="Smith Family" --username=demo --server=False

python3 -m gprime.app --database="Smith Family" --import-file="myinfo.gramps" --username=demo --server=False

python3 -m gprime.app --database="Smith Family" --username=demo

python3 -m gprime.app --help
```
