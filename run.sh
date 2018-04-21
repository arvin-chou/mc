#! /bin/bash

# run server, default is 8080
PWD=`pwd`
CONFIG_PWD=${PWD}/config/nginx
sudo nginx -s stop
sudo nginx -p ${CONFIG_PWD} -c ${CONFIG_PWD}/nginx.conf

# run middle ware
# if uwsgi not found, plz excutes `source mc/bin/activate`
#EVN="settings/mysql.py" uwsgi --pyargv "settings=settings/mysql.py" uwsgiconfig.ini 
uwsgi -H mc --pyargv "settings=settings/mysql.py" uwsgiconfig.ini 
#uwsgi uwsgiconfig.ini 
