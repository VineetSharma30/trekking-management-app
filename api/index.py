import os
import sys
from urllib.parse import parse_qs, urlencode

# Add project root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelRouteFixMiddleware:
    """
    Middleware that captures the original requested route from Vercel's rewrite query parameter
    and sets PATH_INFO so Flask routes all endpoints correctly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        if '__vercel_route__=' in qs:
            params = parse_qs(qs, keep_blank_values=True)
            if '__vercel_route__' in params:
                route = params.pop('__vercel_route__')[0]
                if not route.startswith('/'):
                    route = '/' + route
                environ['PATH_INFO'] = route
                environ['QUERY_STRING'] = urlencode(params, doseq=True)
        elif environ.get('PATH_INFO') in ('/api/index', '/api/index.py', '/api'):
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelRouteFixMiddleware(app.wsgi_app)
