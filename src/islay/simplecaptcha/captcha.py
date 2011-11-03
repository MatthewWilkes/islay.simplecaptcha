from lxml import html
from lxml.etree import XMLSyntaxError, Element
from webob import Request, Response

def CaptchaFactory(global_config, **local_conf):
    return CaptchaMiddleware

class CaptchaMiddleware(object):
    """An endpoint"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Before we go any further, gzip is hard to parse, don't ask for it
        del environ['HTTP_ACCEPT_ENCODING']
        
        request = Request(environ)
        response = request.get_response(self.app)
        if response.content_type == 'text/html':
            # We don't want to deal with images and the like
            try:
                parsed = html.fromstring(response.body)
            except (XMLSyntaxError, TypeError):
                return response(environ, start_response)
            forms = parsed.xpath("//form")
            index = 0
            for form in forms:
                box_id = "captcha%d" % index
                checkbox = Element("input", type="checkbox", name="isHuman", value="1", id=box_id)
                label = Element("label", attrib={'for':box_id})
                label.text = "I am a human"
                length = len(form.getchildren())
                if length == 1:
                    # Hack to add the captcha at the end of single element forms
                    length = 2
                form.insert(length - 1, checkbox) # The submit button is probably last
                form.insert(length, label)
            response.body = html.tostring(parsed)
        return response(environ, start_response)
    
