# gprime

gprime is a web-based application for genealogy. It uses the Gramps API for data, reports, import/export, etc.

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
cd gprime
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

* --database
* --username
* --password
* --debug
* --port
* --hostname
* --sitename
* --data_dir
* --home_dir
* --xsrf

Common variations
-----------------

```shell
PYTHONPATH=/path/to/gprime python3 -m gprime.app --database="Smith Family" --username=demo

python3 -m gprime.app --help

python3 -m gprime.app --debug --base_dir=/path/to/templates --database="Smith Family" --username=demo
```
