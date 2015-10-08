# -*- coding: utf-8 -*-

import json
import os
import time
import pprint

from game_event import dict2obj
from connection import Connection


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, unicode):
            return obj.encode(u'utf8'), True, False

        return pprint.PrettyPrinter.format(self, obj, context, maxlevels, level)


class GameItemReader(object):
    def __init__(self):
        self.content_dict = {}
        self.contents = None

    def get(self, item_id):
        item_id = str(item_id).lstrip(u'@')
        return dict2obj(self.content_dict.get(item_id))

    def get_name(self, item):
        return self.get(item.item).name

    def read(self, filename):
        with open(filename) as f:
            self.contents = json.load(f)
        for content in self.contents:
            if 'id' in content:
                self.content_dict[content['id']] = content

    @staticmethod
    def get_modification_time(filename):
        try:
            return time.localtime(os.path.getmtime(filename))
        except OSError:  # no such file
            return

    def download(self, filename):
        last_modified_time = self.get_modification_time(filename)
        url = 'http://java.shadowlands.ru/zombievk/items'
        data = Connection(url).get_changed_document(
            data={'lang': 'ru'},
            last_client_time=last_modified_time
        )
        with open(filename, 'w') as f:
            f.write(data.encode(u'utf-8'))

    def pretty_write(self, filename):
        with open(filename, 'w') as f:
            pretty_dict = MyPrettyPrinter().pformat(self.content_dict)
            f.write(pretty_dict)
