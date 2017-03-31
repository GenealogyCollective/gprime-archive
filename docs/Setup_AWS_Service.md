# Setup an AWS service

These are notes on using Amazon Web Services (yum-based install). Everything below works, unless otherwise noted.

1. Get a DNS name ($12, used gprime.info)
2. Get a Reserved Instance (make a particular type, m2.mirco) ($95 compute cloud)
3. Make an instance (of same type, m2.micro)
4. Get an Elastic IP
5. Associate subdomain with instance
6. Add Elastic IP to DNS subdomain
6. Enable SSH on something (work in progress)

Get Connect info for instance. Login (ssh) and run the following:

Redhat-based systems:

```shell
sudo service httpd stop

sudo yum update
sudo yum install python35.x86_64
sudo yum install python35-devel
sudo yum install git
sudo yum install emacs
sudo yum install python35-pip
sudo yum install gettext
sudo yum install intltool
sudo yum install libicu
sudo yum install libicu-devel.x86_64
sudo yum install gcc
sudo yum install gcc-c++
```
Ubuntu-based systems:

```shell
sudo apt update

sudo apt install python-dev
sudo apt install git
sudo apt install emacs
sudo apt install gettext
sudo apt install intltool
sudo apt install gcc
sudo apt install g++

sudo apt install libicu-dev 
sudo apt install python3-pip
```

Python setup:

```
sudo python3 -m pip install pip -U
sudo /usr/local/bin/pip3.5 install pyicu

git clone --depth=10 https://github.com/genealogycollective/gprime
cd gprime
sudo /usr/local/bin/pip3.5 install . -U

cd
gprime --site-dir=family_tree --create="Demo Family"
gprime --site-dir=family_tree --add-user=demo --password=demo

sudo /usr/local/bin/gprime --site-dir=family_tree --open-browser=0 --port=80 &
```
