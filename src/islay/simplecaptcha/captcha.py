from webob import Request, Response

def CaptchaFactory(global_config, **local_conf):
    return CaptchaMiddleware

class CaptchaMiddleware(object):
    """An endpoint"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        request = Request(environ)
        response = request.get_response(self.app)
        return response(environ, start_response)