import tornado.wsgi

import sae
import webmain

application = sae.create_wsgi_app(tornado.wsgi.WSGIApplication(webmain.url, **webmain.settings))