import urllib

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

        if request.method == "POST":
            valid = 'isHuman' in request.POST
            if not valid:
                params = urllib.urlencode(request.POST)
                if request.referrer is None:
                    # huh....
                    raise ValueError
                from_page = request.referrer.split("?")[0] + "?" + params
                response = Response(status=302, location=from_page)
                return response(environ, start_response)
            else:
                post = request.POST.copy()
                del post['isHuman']
                request.body = urllib.urlencode(post)
        
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
                if form.method.upper() == "GET":
                    continue
                try:
                    tags = [child for child in form.iterdescendants() if child.tag=='input']
                    submit = tags[-1] # maybe?
                except IndexError:
                    # Empty forms are weird.
                    continue
                
                box_id = "captcha%d" % index
                index += 1
                checkbox = Element("input", type="checkbox", name="isHuman", value="1", id=box_id)
                label = Element("label", attrib={'for':box_id})
                label.text = "I am a human"

                submit.addprevious(checkbox)
                submit.addprevious(label)
            response.body = html.tostring(parsed)
        return response(environ, start_response)
    
