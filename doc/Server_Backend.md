# Websever and Flask Web API setup

The server architecure is an Apache Webserver virtual host acting as a reverse proxy to a Python Flask application through
Apache's WSGI module.

## Apache configuration
Most of the for the University systems is done by following the steps found [here](https://warwick.ac.uk/fac/sci/dcs/intranet/user_guide/apache/)
If running this on a non-University system, the steps are as follows:
 1. Install Apache - the details of this depend on the operating system.
 2. Install the Apache mod_wsgi module, or [compile it yourself](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html), making sure to do so with Python 3.x.
 3. Install the [Flask Python Package](https://flask.palletsprojects.com/en/1.1.x/installation/#installation) using `pip3.6 install flask`.
 4. Add the following to the `httpd.conf` file in your Apache installation, replacing ROOT DIR with the absolute path of the top level directory of the project repository:
 ```conf
 # Load the WSGI module
LoadModule wsgi_module modules/mod_wsgi.so
<VirtualHost *:80>
     # Add machine's IP address (use ifconfig command)
     ServerName x.x.x.x
     WSGIScriptAlias /api [ROOT DIR]/src/www/wsgi.py
     <Directory [ROOT DIR]/src/www/app>
            Options FollowSymLinks
            AllowOverride None
            Require all granted
     </Directory>
     ErrorLog ${APACHE_LOG_DIR}/error.log
     LogLevel warn
     CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
 ```

The Apache config for the University machine is as follows:
```conf
LoadModule wsgi_module modules/mod_wsgi.so
WSGISocketPrefix [APACHE INSTALL DIR]/run/wsgi
WSGIDaemonProcess access-toold user=[USER] group=dcsstaff threads=2
WSGIScriptAlias /api [ROOT DIR]/src/www/wsgi.py
```

## wsgi.py Setup

The `wsgi.py`file under `src/www/wsgi.py` should be configured as follows:
```python
import sys
import site

# Activate the virtualenv when serving the app
activate_this = '[ROOT DIR]/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

site.addsitedir('[ROOT DIR]/venv/lib/python3.6/site-packages')
sys.path.insert(0, '[ROOT DIR]src/www')

from app import app as application
```

## Flask App Setup
The Flask application contains its own `.env` file for system variables relating to the Flask app.
These are loaded into an Flask app instance through `config.py`.
The file should be filled in as follows:
```
# The python file which starts a local flask server. Enables the usage of `flask run`
FLASK_APP=run.py
# Port to run the flask app on
PORT=7162
# The path to the SQLite database or URL through which to access your DB system
DATABASE_URL=
# Population metrics known by the system. If adding a new metric this needs to be implemented in `views.py` under the `/population-metrics` route.
POPULATION_METRICS=["population_density", "at-risk_score"]
```

## Webserver API
To see information abount endpoints implemented in views.py, open the API reference JSON found in `reference/` in [stoplight.io studio](https://stoplight.io/studio/).
