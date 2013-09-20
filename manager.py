# coding: utf-8

from sitelib import Site, BTSSite, RMSite
from csvlib import CSV, BTSCSV, RMCSV

class Manager:
    site = None
    csv = None
    def download(self):
        self.site.login()
        response = self.site.request()
        self.csv.set(response)
    
    def cleanse(self):
        self.csv.cleanse()

    def save(self):
        self.csv.save()

class BTSManager(Manager):

    def __init__(self):
        user = config['bts']['user']
        pwd = config['bts']['pwd']
        filename = config['bts']['filename']
        self.site = BTSSite(user, pwd)
        self.csv = BTSCSV(filename)

class RMManager(Manager):
    def __init__(self):
        user = config['rm']['user']
        pwd = config['rm']['pwd']
        filename = config['rm']['filename']
        self.site = RMSite(user, pwd)
        self.csv = RMCSV(filename)

if __name__ == '__main__':
    for manager in [BTSManager(), RMManager()]:
        manager.download()
        manager.cleanse()
        manager.save()