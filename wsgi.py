import site

# Activate the virtualenv when serving the app
activate_this = '/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

site.addsitedir('/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/venv/lib/python3.6/site-packages')

from app import app as application
