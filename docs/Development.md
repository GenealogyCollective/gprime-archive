gPrime Development
------------------

To work on gPrime, you'll need a Python3 environment. On Windows and Mac, perhaps the easiest method of using gPrime is to start with an [Anaconda Python3 environment](https://www.continuum.io/downloads).
 
To install gPrime from github sources:

```
git clone  https://github.com/GenealogyCollective/gprime
cd gprime
```

To run gPrime without installing it (you may need to use `python3):

```
export PYTHONPATH=/path/to/gprime-source-dir
python -m gprime.app --site-dir="family_tree"
```

During development, there is a `--debug` flag. This does two things:

* will automatically reload all files and templates if they are changed
* will print out debugging messages (such as all database access queries)

For information on working on translations, see: 

https://github.com/GenealogyCollective/gprime/blob/master/docs/Translations.md

## gPrime 2.0

To use the node development tools:

1. Find out latest nvm version:
  * go to https://github.com/creationix/nvm/releases
1. curl https://raw.githubusercontent.com/creationix/nvm/v0.33.1/install.sh | bash
1. source ~/.bashrc
1. nvm install 5
1. nvm use 5
