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
                    writer = csv.writer(
                        fout, quoting=csv.QUOTE_ALL)
                    writer.writerows(self._rows)
                except csv.Error, error:
                    print 'ERROR: file %s: %s' % (self._filename, error)
        except IOError, error:
            print 'ERROR: file %s: %s' % (self._filename, error)

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

    def cleanse(self):
        lines = [','.join(row) for row in self._rows]
        selected_lines = [line for line in lines
            if re.match(r'^[\w|\d]{32}', line) is not None]
        self._rows = [row[:12] for row in csv.reader(selected_lines)
            if self._can_strptime(row[9])]

class BTSHTMLCSV(BTSCSV):
    _pattern = re.compile(
        r'<td>(\d+)</td><td><a href=".*id=(\w{32})[^>]*>([^<]+)</a></td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td>')
    def set(self, readable):
        readable.seek(0)
        html_source = re.sub(r'</?font[^>]*>', '', readable.read())
        html_source = html_source.decode('utf8').encode('sjis')
        self._rows = self._pattern.findall(html_source)

    def cleanse(self):
        pass

class RMCSV(CSV):
    def cleanse(self):
        self._rows = [
                [data.replace('\r', '\2').replace('\n', '\3') for data in row]
            for row in self._rows]
