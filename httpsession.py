# coding: utf-8
import urllib, urllib2, cookielib, re

def _default_headers():
    return {
        'Content-Type':'application/x-www-form-urlencoded',
        'Accept':'text/html,application/xhtml+xml,application/xml',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
        'Accept-Encoding':'gzip,deflate,sdch',
        'Connection':'keep-alive',
    }

def _build_opener():
    opener = urllib2.build_opener()
    opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    return opener

def _extract_hidden_value(content):
    pattern = re.compile(
        r'<input type="hidden" name="(?P<name>.+)" id="(?P<id>.+)" value="(?P<value>.*)" />')
    for m in pattern.finditer(content):
        yield (m.group('name'), m.group('value'))

def extract_hidden_value(content):
    return dict((v for v in _extract_hidden_value(content)))

class Session:
    __attrs__ = [
        'headers',
        'opener',
    ]

    def __init__(self):
        self.headers = _default_headers()
        self.opener = _build_opener()

    def __del__(self):
        self.close()

    def close(self):
        self.opener.close()

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def request(self, method, url, 
        params={},
        headers={}):
        if method.upper() == 'POST':
            data = urllib.urlencode(params)
            request = urllib2.Request(url, data=data, headers=headers)
        elif method.upper() == 'GET':
            request = urllib2.Request(url, headers=headers)
        else: raise Exception('Not supported method.')
        response = self.opener.open(request)
        return type('Response', (), {
            'code':response.code,
            'content':response.read(),
            'headers':dict(response.headers),
            'url':response.url,
        })