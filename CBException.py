# coding: utf-8

class CBException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, 'CBException: ' + msg)
