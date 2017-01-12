gPrime Development
------------------

To work on gPrime, you'll need a Python3 environment. On Windows and Mac, perhaps the easiest method of using gPrime is to start with an [Anaconda Python3 environment](https://www.continuum.io/downloads).
 
To install gPrime from github sources:

```
git clone  https://github.com/GenealogyCollective/gprime
cd gprime
```

To run gPrime without installing it (you may need to use `python3` in this example):

```
export PYTHONPATH=/path/to/gprime-source-dir
python -m gprime.app --site-dir="family_tree"
```

During development, there is a `--debug` flag. This does two things:

* will automatically reload all files and templates if they are changed
* will print out debugging messages (such as all database access queries)

For information on working on translations, see: 

https://github.com/GenealogyCollective/gprime/blob/master/docs/Translations.md
