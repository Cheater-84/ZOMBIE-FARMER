# -*- coding: utf-8 -*-

import os
from sqlite3 import connect

    
class StatisticAccess(object):

    def __init__(self, account):

        self.db_name = '%s/params/db/stat_%s.db' % (os.getcwd(), account.user_name)
        self.conn = connect(self.db_name)
        self.cursor = self.conn.cursor()

        self.params = account.params()

        query = 'SELECT COUNT(name) FROM sqlite_master WHERE name = "users"'
        self.cursor.execute(query)
        row_counts = [row[0] for row in self.cursor]

        self.table_ready = bool(row_counts[0])

        self.status_enum = {
            'NOT_CHECKED': 0, 'NOT_OPEN': 1, 'OPENED': 2, 'PLATFORM': 3, 'VALRIGHT': 4, 'JAPAN': 5, 'HYPER': 6, 'FISHER': 7
        }

    def get_user_dict(self, param_name):

        res = {}

        query = 'SELECT COUNT(name) FROM sqlite_master WHERE name = "users"'
        self.cursor.execute(query)
        row_counts = [row[0] for row in self.cursor]

        if not row_counts[0]:
            return res

        for island in self.params.statistic_islands:
            user_pack = []

            query = 'SELECT uid, %s FROM users WHERE %s > 7' % (island, island)
            self.cursor.execute(query)

            for row in self.cursor:
                value = row[1]
                uid = row[0]

                if value & (1 << self.status_enum.get(param_name)):
                    user_pack.append(unicode(uid))

            if user_pack:
                res[island] = user_pack
        return res

    def get_user_island(self, island, param_name):

        res = {}
        user_pack = []

        query = 'SELECT COUNT(name) FROM sqlite_master WHERE name = "users"'
        self.cursor.execute(query)
        row_counts = [row[0] for row in self.cursor]

        if not row_counts[0]:
            return user_pack

        query = 'SELECT uid, %s FROM users WHERE %s > 7' % (island, island)
        self.cursor.execute(query)

        for row in self.cursor:
            value = row[1]
            uid = row[0]

            if value & (1 << self.status_enum.get(param_name)):
                user_pack.append(unicode(uid))

        if user_pack:
            res[island] = user_pack

        return res
