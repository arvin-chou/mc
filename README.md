# Flask-RESTful

[![Build Status](https://travis-ci.org/flask-restful/flask-restful.svg?branch=master)](http://travis-ci.org/flask-restful/flask-restful)
[![Coverage Status](http://img.shields.io/coveralls/flask-restful/flask-restful/master.svg)](https://coveralls.io/r/flask-restful/flask-restful)
[![PyPI Version](http://img.shields.io/pypi/v/Flask-RESTful.svg)](https://pypi.python.org/pypi/Flask-RESTful)
[![PyPI Downloads](http://img.shields.io/pypi/dm/Flask-RESTful.svg)](https://pypi.python.org/pypi/Flask-RESTful)

Flask-RESTful provides the building blocks for creating a great REST API.

## TODO
[apns](https://github.com/djacobs/PyAPNs)
[Gunicorn](http://alexandersimoes.com/hints/2015/10/28/deploying-flask-with-nginx-gunicorn-supervisor-virtualenv-on-ubuntu.html)
[Flask + Gunicorn + Nginx 部署](http://www.cnblogs.com/Ray-liang/p/4837850.html)


## User Guide

You'll find the user guide and all documentation [here](http://flask-restful.readthedocs.org/en/latest/)

* Requirements 

# dp

dp is an example Flask application illustrating some of my common practices

## Development Environment

At the bare minimum you'll need the following for your development environment:

1. [Python](http://www.python.org/)
2. [MySQL](http://www.mysql.com/)
3. [Redis](http://redis.io/)

It is strongly recommended to also install and use the following tools:

1. [virtualenv](https://python-guide.readthedocs.org/en/latest/dev/virtualenvs/#virtualenv)
2. [virtualenvwrapper](https://python-guide.readthedocs.org/en/latest/dev/virtualenvs/#virtualenvwrapper)
3. [Vagrant](http://vagrantup.com)
3. [Berkshelf](http://berkshelf.com)

### Local Setup

The following assumes you have all of the recommended tools listed above installed.

#### 1. Clone the project:

    $ git clone https://github.com/arvin-chou/mc.git
    $ cd mc

#### 1.1 prepared environment
    $ apt-get install python3
    $ apt-get install python3-pip
    $ pip3 install virtualenv uwsgi
    $ apt-get install python-software-properties
    $ add-apt-repository ppa:gias-kay-lee/npm
    $ apt-get update
    $ apt-get install npm

#### 1.2 do more
    $ apt-get install zsh
    $ sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
    $ wget https://gist.githubusercontent.com/phawk/b2b3f1e28f8ffc33b396/raw/41772b8df50395dff3f0281ccde4ab723f1c466e/.screenrc -O ~/.screenrc

#### 2. Create and initialize virtualenv for the project:

    $ LC_ALL=C virtualenv mc
    $ source mc/bin/activate
    $ pip uninstall werkzeug
    $ pip install werkzeug==0.10

#### 2.1 install Pillow
    $ apt-get install build-essential curl git m4 ruby texinfo libbz2-dev libcurl4-openssl-dev libexpat-dev libncurses-dev zlib1g-dev
    $ git clone https://github.com/Homebrew/linuxbrew.git ~/.linuxbrew
    $ export PATH="$HOME/.linuxbrew/bin:$PATH"
    $ export MANPATH="$HOME/.linuxbrew/share/man:$MANPATH"
    $ export INFOPATH="$HOME/.linuxbrew/share/info:$INFOPATH"
    $ brew install libjpeg zlib

#### 2.2 install Dependency
    $ python3 ./setup.py install
    $ pip install -r requirements.txt # if setup fail

#### 2.3 Install nginx 1.9.15
    # [How to install nginx 1.9.5 with HTTP2 support on Ubuntu 14.04 LTS](https://by-example.org/install-nginx-with-http2-support-on-ubuntu-14-04-lts/)
    $ vim /etc/apt/sources.list 
    # add ```
    deb http://nginx.org/packages/mainline/ubuntu trusty nginx
    deb-src http://nginx.org/packages/mainline/ubuntu trusty nginx
    ```
    $ wget -q -O- http://nginx.org/keys/nginx_signing.key | sudo apt-key add -
    $ apt-get update
    $ apt-get install nginx
#### 2.2 Create Mysql 5.7.12 
    # [How To Install MySQL on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-14-04)
    $ wget http://dev.mysql.com/get/mysql-apt-config_0.6.0-1_all.deb
    $ dpkg -i mysql-apt-config_0.6.0-1_all.deb
    $ apt-get update
    $ apt-get install mysql-server
    ```
    // in mysql shell
    mysql> create database Merchant;
    mysql> grant all on Merchant.* to 'Merchant_user'@'localhost' identified by "password";
    mysql> flush privileges;
    // hack uft-8 default in my.cnf
    [client]
    default-character-set = utf8

    [mysqld]
    character-set-client-handshake=FALSE
    init_connect = SET collation_connection = utf8_general_ci
    init_connect = SET NAMES utf8
    character-set-server = utf8
    collation-server = utf8_general_ci
    ```

#### 3. Install the required cookbooks:

    $ berks install

#### 4. Install the Berkshelf plugin for Vagrant:

    $ vagrant plugin install vagrant-berkshelf

#### 5. Start virtual machine:

    $ vagrant up

#### 6. Upgrade the database:

    $ alembic upgrade head

#### 7. Run the development server:

    (mc) $ run.sh

#### 8. In another console run the Celery app:

    $ celery -A mini-restful.tasks worker

#### 9. Open [http://localhost:5000](http://localhost:5000)

### 10. install apidoc
    $ npm config set strict-ssl false
    $ npm install apidoc
    $ apt-get install nodejs-legacy
    $ npm cache clean -f
    $ npm install -g n
    $ n stable
    $ IP="localhost" ./scripts/genapidoc.sh # change to your target ip / dns
    $ # open apidoc/index.html

### Development

1. create dictionary under ${ROOT}/module and module name as ```module name```,
  for example, we create policy under ${ROOT}/module/policy.
2. the module folder at least contains with three files: sql.py, model.py,
  __init__.py.
  - sql.py was called by ${ROOT}/config/config.py when server runs and it could
  initialize database.
  - model.py was called by run.py which could route to the model by path.
  - __init__.py contains common variables such as table name, request/response json head
  used in model.py/sql.py/unittest

3. add routing rules in run.py and request path to ${ROOT}/config/config.py
#### Database Migrations

This application uses [Alembic](http://alembic.readthedocs.org/) for database
migrations and schema management. Changes or additions to the application data
models will require the database be updated with the new tables and fields.
Additionally, ensure that any new models are imported into the consolidated
models file at `overholt.models`. To generate a migration file based on the
current set of models run the following command:

    $ alembic revision --autogenerate -m "<a description of what was modified>"

Review the resulting version file located in the `alembic/versions` folder. If
the file is to your liking upgrade the database with the following command:

    $ alembic upgrade head

For anything beyond this workflow please read the Alembic documentation.

#### Management Commands

Management commands can be listed with the following command:

    $ python manage.py

These can sometimes be useful to manipulate data while debugging in the browser.


#### Tests

To run the tests use the following command:

    $ EVN="settings/test.py" python3 ./setup.py test
