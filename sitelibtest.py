# coding: utf-8
from sitelib import BTSSite
import json
import ipdb
config = json.load(open('config.json', 'r'))

site = BTSSite(config['bts']['user'], config['bts']['pwd'])
site.login()
ipdb.set_trace()
io = site.request()
print io.getvalue()
