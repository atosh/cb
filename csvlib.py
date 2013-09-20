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
        try:
            with open(self._filename, 'rb') as fin:
                reader = csv.reader(fin)
                try:
                    self._rows = [row for row in reader]
                except csv.Error, error:
                    print 'ERROR: file %s, line %d: %s' % (
                        self._filename, reader.line_num, error)
        except IOError, error:
            print 'ERROR: file %s: %s' % (self._filename, error)

    def save(self):
        try:
            with open(self._filename, 'wb') as fout:
                try:
                    writer = csv.writer(fout)
                    writer.writerows(self._rows)
                except csv.Error, error:
                    print 'ERROR: file %s: %s' % (self._filename, error)
        except IOError, error:
            print 'ERROR: file %s: %s' % (self._filename, error)

    def cleanse(self):
        raise NotImplementedError('Should impl this.')

from datetime import datetime as dt
class BTSCSV(CSV):
    _template = '%Y/%m/%d %H:%M:%S'
    def _can_strptime(self, tstr):
        try:
            dt.strptime(tstr, self._template)
        except ValueError:
            return False
        return True
    
    def cleanse(self):
        raise NotImplementedError('不具合あり')
        string_io = StringIO()
        writer = csv.writer(string_io)
        writer.writerows(self._rows)
        # タグを除去
        pattern = re.compile(r'<[^>]*?>')
        buf = pattern.sub('', string_io.getvalue())
        string_io = StringIO(buf)
        # len(row) >= 12のものを残し、さらにrow[9]が日付のものを残す
        self._row = [row for row in csv.reader(string_io)
            if len(row) >= 12 and self._can_strptime(row[9])]

class RMCSV(CSV):
    def cleanse(self):
        # \r\n を \2\3 に変更
        self._rows = [
                [data.replace('\r', '\2').replace('\n', '\3') for data in row]
            for row in self._rows]
