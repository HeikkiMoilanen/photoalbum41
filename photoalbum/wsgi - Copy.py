"""
WSGI config for photoalbum project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
#the next 3 lines are for Heroku
#from django.core.wsgi import get_wsgi_application
#from dj_static import Cling
#application = Cling(get_wsgi_application())

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "photoalbum.settings")

#These were before Heroku
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
