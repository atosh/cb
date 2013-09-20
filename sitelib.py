# coding: utf-8

import urllib, httplib, re, StringIO

class Site:
    _user = ''
    _pwd = ''
    _connection = None
    _headers = {}

    def _extract_cookie(self, response):
        cookies = response.getheader('Set-Cookie').split(',')
        return ';'.join([cookie.split(';')[0] for cookie in cookies])

    def __init__(self, user, pwd):
        self._user = user
        self._pwd = pwd
    
    def login(self):
        raise NotImplementedError('Should impl this.')
    
    def logout(self):
        self._connection.close()
        del(self._headers['Cookie'])

    def request(self):
        raise NotImplementedError('Should impl this.')

class BTSSite(Site):
    _host = 'bugtrack.wingarc.co.jp'
    _headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'Connection': 'keep-alive',
        "Accept": "text/plain",
    }
    _connection = httplib.HTTPConnection(_host)

    _pattern = re.compile(
        r'<input.+type="hidden".+name="([^"]+)".+value="([^"]+)?".+?>')
    
    def _extract_hidden_value(self, contents, data):
        for m in self._pattern.finditer(contents):
            data[m.group(1)] = m.group(2)
        return data

    def login(self):
        path = '/DrSum/login.aspx'
        self._connection.request('GET', path, headers=self._headers)
        response = self._connection.getresponse()
        contents = response.read()
        postdata = {
            'txtUserID':self._user,
            'txtUserPass':self._pwd,
            'btnLogin':'ログイン',
        }
        postdata = self._extract_hidden_value(contents, postdata)
        params = urllib.urlencode(postdata)
        self._connection.request('POST', path, params, self._headers)
        response = self._connection.getresponse()
        contents = response.read()
        cookie = self._extract_cookie(response)
        self._headers['Cookie'] = cookie

    def request(self):
        path = '/DrSum/support/ProjectList.aspx?projectID=12c90e47d7284500b7568d3f82e00d12'
        self._connection.request('GET', path, headers=self._headers)
        response = self._connection.getresponse()
        contents = response.read()
        postdata = {
            'ctl00$ContentPlaceHolder1$txtNo':'',
            'ctl00$ContentPlaceHolder1$ddlType':'all',
            'ctl00$ContentPlaceHolder1$ddlCategory':'all',
            'ctl00$ContentPlaceHolder1$ddlSeverity':'all',
            'ctl00$ContentPlaceHolder1$ddlStatus':'all',
            'ctl00$ContentPlaceHolder1$ddlCreator':'all',
            'ctl00$ContentPlaceHolder1$txtIncKeyword':'',
            'ctl00$ContentPlaceHolder1$txtNotIncKeyword':'',
            'ctl00$ContentPlaceHolder1$ddlPageRecordCount':'10',
            'ctl00$ContentPlaceHolder1$btsCsv':'CSV出力',
        }
        postdata = self._extract_hidden_value(contents, postdata)
        params = urllib.urlencode(postdata)
        self._connection.request('POST', path, params, self._headers)
        response = self._connection.getresponse()
        return StringIO.StringIO(response.read())

class RMSite(Site):
    _host = 'fcredmine'
    _headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'Connection': 'keep-alive',
        "Accept": "text/plain",
    }
    _connection = httplib.HTTPConnection(_host)

    def _extract_auth_token(self, contents):
            m = re.search(
                r'<input name="authenticity_token".+value="(.+)" />',
                contents)
            if m is None:
                raise httplib.HTTPException(
                    'authenticity_token has not been set.')
            return m.group(1)

    def login(self):
        path = '/login'
        self._connection.request('GET', path, headers=self._headers)
        response = self._connection.getresponse()
        contents = response.read()
        self._headers['Cookie'] = self._extract_cookie(response)
        auth_token = self._extract_auth_token(contents)
        postdata = {
            'username':self._user,
            'password':self._pwd,
            'authenticity_token':auth_token,
        }
        params = urllib.urlencode(postdata)
        self._connection.request('POST', path, params, self._headers)
        response = self._connection.getresponse()
        contents = response.read()
        self._headers['Cookie'] = self._extract_cookie(response)

    def request(self):
        path = '/projects/mb/issues.csv'
        self._connection.request('GET', path, headers=self._headers)
        response = self._connection.getresponse()
        return StringIO.StringIO(response.read())

