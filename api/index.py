import os
import sys

# Add project root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelPathFixMiddleware:
    """
    WSGI middleware for Vercel Serverless Functions.
    Vercel rewrites requests to /api/index.py, which sets PATH_INFO to '/api/index.py'.
    This middleware extracts the actual requested path from HTTP_X_MATCHED_PATH or
    HTTP_X_VERCEL_REWRITE_URL, ensuring Flask routes match correctly.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH') or environ.get('HTTP_X_VERCEL_REWRITE_URL')
        if matched_path:
            environ['PATH_INFO'] = matched_path.split('?')[0]
        elif environ.get('PATH_INFO') in ('/api/index.py', '/api/index', '/api'):
            environ['PATH_INFO'] = '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
