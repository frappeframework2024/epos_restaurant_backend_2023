from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
import os

class FileRedirectMiddleware:
    def __init__(self, app, site_path):
        self.app = app
        self.site_path = site_path

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.path.startswith('/files/'):
            filename = request.path.split('/files/')[-1]
            filepath = os.path.join(self.site_path, 'public', 'files', filename)
            if not os.path.exists(filepath):
                # Redirect to fallback image
                fallback = '/files/preview.png'
                res = Response('', status=302)
                res.headers['Location'] = fallback
                return res(environ, start_response)

        return self.app(environ, start_response)
