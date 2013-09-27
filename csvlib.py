# coding: utf-8

import csv
import re
from StringIO import StringIO

class CSV:
    _rows = [[]]

    def __init__(self, filename):
        self._filename = filename

    def set(self, readable):
        reader = csv.reader(readable)
        self._rows = [row for row in reader]

    def load(self):
        with open(self._filename, 'rb') as fin:
            reader = csv.reader(fin)
            self._rows = [row for row in reader]

    def save(self):
        with open(self._filename, 'wb') as fout:
            writer = csv.writer(
                fout, quoting=csv.QUOTE_ALL)
            writer.writerows(self._rows)

    def cleanse(self):
        raise NotImplementedError('Should impl this.')

from datetime import datetime
class BTSCSV(CSV):
    _template = '%Y/%m/%d %H:%M:%S'
    def _can_strptime(self, tstr):
        try:
            datetime.strptime(tstr, self._template)
        except ValueError:
            return False
        return True

    def _manage_comma_in_title(self, row):
        subrow = row[3:]
        candidates = ['サポート', 'サポート★', '改修要望']
        while len(subrow) >= 2 and not subrow[1].decode('sjis').encode('utf8') in candidates:
            subrow = [','.join(subrow[0:2])] + subrow[2:]
        ret = row[:3] + subrow
        return ret[:12]

    def cleanse(self):
        #import ipdb; ipdb.set_trace()
        lines = [','.join(row) for row in self._rows]
        selected_lines = [line for line in lines
            if re.match(r'^[\w|\d]{32}', line) is not None]
        self._rows = [self._manage_comma_in_title(row) for row in csv.reader(selected_lines)]

class RMCSV(CSV):
    def cleanse(self):
        self._rows = [
                [data.replace('\r', '\2').replace('\n', '\3') for data in row]
            for row in self._rows]
