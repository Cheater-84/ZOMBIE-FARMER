# -*- coding: utf-8 -*-

from master import MasterAccount
from params import Params


class AccountDemo(MasterAccount):
    user_name = 'demo'
    user_login = ''
    user_password = ''
    params = Params


class Accounts(object):
    accounts = [
        AccountDemo
    ]
