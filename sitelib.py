# coding: utf-8

import httpsession
import re
from StringIO import StringIO

def _extract_hidden_value(content):
    pattern = re.compile(
        r'<input type="hidden" name="(?P<name>.+)" id="(?P<id>.+)" value="(?P<value>.*)" />')
    for m in pattern.finditer(content):
        yield (m.group('name'), m.group('value'))

def extract_hidden_value(content):
    return dict((v for v in _extract_hidden_value(content)))

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

import urllib2, cookielib
class BTSSite(Site):
    host = 'bugtrack.wingarc.co.jp'
    path = '/DrSum/support/ProjectList.aspx?projectID=12c90e47d7284500b7568d3f82e00d12'
    url = 'http://' + host + path
    session = httpsession.Session()
    response = None
    
    def login(self):
        self.response = self.session.get(self.url)
        params = extract_hidden_value(self.response.content)
        params.update({
            '__LASTFOCUS':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            'txtUserID':self._user,
            'txtUserPass':self._pwd,
            'btnLogin':'ログイン',
        })
        self.response = self.session.post(self.response.url, params=params)

    def request(self):
        params = extract_hidden_value(self.response.content)
        params.update({
            '__EVENTTARGET':'ctl00$ContentPlaceHolder1$GridView1',
            'ctl00$ContentPlaceHolder1$ddlStatus':'all',
            'ctl00$ContentPlaceHolder1$ddlPageRecordCount':'100',
            'ctl00$ContentPlaceHolder1$btsCsv':'CSV出力',
        })
        self.response = self.session.post(self.url, params=params)
        return StringIO(self.response.content)

class RMSite(Site):
    host = 'fcredmine'
    session = httpsession.Session()
    response = None

    def _extract_auth_token(self, content):
            m = re.search(
                r'<input name="authenticity_token".+value="(.+)" />',
                content)
            if m is None:
                raise Exception('authenticity_token has not been set.')
            return m.group(1)

    def login(self):
        path = '/login'
        url = 'http://' + self.host + path
        self.response = self.session.get(url)
        content = self.response.content
        auth_token = self._extract_auth_token(content)
        params = {
            'username':self._user,
            'password':self._pwd,
            'authenticity_token':auth_token,
        }
        self.response = self.session.post(url, params=params)
        content = self.response.content

    def request(self):
        path = '/projects/mb/issues?query_id=40'
        url = 'http://' + self.host + path
        self.response = self.session.get(url)
        """
        auth_token = self._extract_auth_token(self.response.content)
        params = {
            'authenticity_token':auth_token,
        }
        """
        path = '/projects/mb/issues.csv'
        url = 'http://' + self.host + path
        self.response = self.session.get(url)
        return StringIO(self.response.content)

