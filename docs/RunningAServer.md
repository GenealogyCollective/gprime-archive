Running gPrime on a Server
==========================

These are notes for running gPrime (and multiple copies of gPrime) on a server, such as Ubuntu. These notes are untested. They will eventually be tested, or removed.

Requirements
------------

* systemd
* apache

In this example, we start up each gPrime server on regular ports (say, in the 8000 range). We then serve HTTPS secure data by redirecting external requests to the 8000-range gPrime servers.

Auto startup: systemd config file
---------------------------------

Place the following in a file such as "/etc/systemd/system/smith_family.service"

```
## systemd config file for starting a gprime server

[Unit]
Description=gPrime Web Server

[Service]
User=dblank
Group=dblank
Environment=PYTHONPATH=/home/dblank/gprime
WorkingDirectory=/home/dblank/gprime-sites
ExecStart=/usr/bin/python3 -m gprime.app --site-dir="Smith_Family" --port=8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Then make a link to this file:

```
cd /etc/systemd/system/multi-user.target.wants/
ln -s /etc/systemd/system/smith_family.service
```

HTTPS
-----

Edit this file:

/etc/apache2/sites-enabled/default-ssl.conf

to contain something like:

```
NameVirtualHost *:443

<IfModule mod_ssl.c>
	<VirtualHost *:443>
		ServerName blank.blankfamily.us
		ServerAdmin webmaster@localhost

		DocumentRoot /var/www/html

		ErrorLog ${APACHE_LOG_DIR}/error.log
		CustomLog ${APACHE_LOG_DIR}/access.log combined

		SSLEngine on

		#SSLCertificateFile	/etc/ssl/certs/ssl-cert-snakeoil.pem
		#SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
		SSLCertificateFile	/etc/ssl/certs/host.pem
		SSLCertificateKeyFile /etc/ssl/private/host.key

		ProxyPreserveHost On

        	ProxyPass / http://127.0.0.1:8003/
		ProxyPassReverse / http://127.0.0.1:8003/

		<FilesMatch "\.(cgi|shtml|phtml|php)$">
				SSLOptions +StdEnvVars
		</FilesMatch>
		<Directory /usr/lib/cgi-bin>
				SSLOptions +StdEnvVars
		</Directory>
	</VirtualHost>
	<VirtualHost *:443>
		ServerName smith.blankfamily.us
        	ProxyPass / http://127.0.0.1:8001/
		ProxyPassReverse / http://127.0.0.1:8001/
	</VirtualHost>
	<VirtualHost *:443>
		ServerName jones.blankfamily.us
        	ProxyPass / http://127.0.0.1:8000/
		ProxyPassReverse / http://127.0.0.1:8000/
	</VirtualHost>
</IfModule>
```

Self-signed certificates
------------------------

Some notes to try:

```
openssl genrsa 2048 > host.key
openssl req -new -x509 -nodes -sha1 -days 3650 -key host.key > host.cert
cat host.cert host.key > host.pem
chmod 400 host.key host.pem 
cp -i host.key /etc/ssl/private/
cp -i host.pem /etc/ssl/certs/
```
or maybe:

```
openssl genrsa -des3 -out host.key 2048 
openssl rsa -in host.key -out host.key.rsa
openssl req -new -key host.key.rsa -out host.csr
openssl x509 -req -extensions v3_req -days 3650 -in host.csr -signkey host.key.rsa -out host.cer -extfile /etc/ssl/openssl.cnf
```

In apache config file, above:

```
		SSLCertificateFile	/etc/ssl/certs/host.pem
		SSLCertificateKeyFile /etc/ssl/private/host.key
```

