import sys
import site

site.addsitedir('/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/venv/lib/python3.6/site-packages')

sys.path.insert(0, '/dcs/project/transport-access-tool/TfWM-Accessibility-Tool/www')

from app import app as application
