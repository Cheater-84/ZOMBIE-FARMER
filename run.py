# -*- coding: utf-8 -*-

import logging

from engine.game_engine import Game
from params.accounts import Accounts
from vk import vkutils
from engine.helpers import prompt_query
import sys
import urllib2
import json
import time

__version__ = 2.2

logger = logging.getLogger(u'main')
accounts = Accounts()

ACTIONS = {
    0: u'Основной режим',
    1: u'Режим обхода соседей',
    2: u'Пиратский режим',
    3: u'Тропический режим',
    4: u'Сбор статистики'
}

REMOTE_SCENARIES = {
    0: u'Положить пряники под елочки',
    1: u'Удобрить деревья соседям',
    2: u'Копать под заданными объектами',
    3: u'Конфисковать мешки без сторожа',
    4: u'Искать сокровища на заданном острове',
    5: u'Обойти торгов в поисках обмена',
    6: u'Стукнуть в башню'
}

REMOTE_DIGGER_PRIORITY = {
    0: u'Японская коллекция',
    1: u'Школьная коллекция',
    2: u'Песочная коллекция',
    3: u'Военная коллекция',
    4: u'Футбольная коллекция, Батарейки',
    5: u'Столовая коллекция',
    6: u'Страшная коллекция, Игрушечная коллекция',
    7: u'Елочная коллекция, Коллекция белого кролика',
    8: u'Гипер коллекция, Секретная коллекция, Коллекция Майа',
    9: u'Любовь, Весенняя коллекция, Коллекция анти-зомби',
    10: u'Скакалки',
    11: u'Мыло',
    12: u'Кафель',
    13: u'Металлолом',
    14: u'Опыт',
    15: u'Бозон Хиггса'
}

REMOTE_TRADER_POSITION = {
    0: u'Купить',
    1: u'Продать'
}

REMOTE_TRADER_PRIORITY = {
    0: u'Японская коллекция',
    1: u'Коллекция палача',
    2: u'Школьная коллекция',
    3: u'Райская коллекция',
    4: u'Коллекция Хэллуина',
    5: u'Изумрудная коллекция'
}


def setup_basic_logging():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)-15s]  %(message)s')
    connection_logger = logging.getLogger(u'connection')
    connection_logger.propagate = False
    connection_logger.addHandler(logging.NullHandler())


if __name__ == '__main__':

    print u'**************************************************\n' \
          u'*                                                *\n' \
          u'*             ZOMBIE FARMER 2.2 (c)              *\n' \
          u'*                                                *\n' \
          u'*    Авторские права: http://vk.com/id8477452    *\n' \
          u'*                                                *\n' \
          u'**************************************************'

    time.sleep(1)
    setup_basic_logging()

    if not len(accounts.accounts):
        sys.stdout.write(u'Не задана ни одна учетная запись')
        raw_input(u'')
        while True:
            pass

    if len(accounts.accounts) == 1:
        account = accounts.accounts[0]()
    else:
        print u'Выберите учетную запись:'
        users = [x.user_name for x in accounts.accounts]
        selected_index = prompt_query(users)
        account = accounts.accounts[selected_index]

    site = vkutils.VK(account)
    request_handler = None

    # Магия, не иначе
    try:
        request_url = 'http://%s:%s/auth?name=%s&login=%s&master_key=%s' % \
                      (account.ip_address, account.port, account.name, account.user_login, account.master_key)
        request = urllib2.Request(request_url)
        request_handler = urllib2.urlopen(request)
    except urllib2.URLError:
        sys.stdout.write(u'Сервер авторизации бота недоступен')
        raw_input(u'')
        sys.exit()

    recv_data = json.loads(request_handler.read())

    if not recv_data.get('auth'):
        account.private_key = None
        sys.stdout.write(recv_data['error'])
        raw_input(u'')
        sys.exit()

    account.private_key = recv_data.get('auth')

    arg_params = dict(mode=0)
    print u'Выберете режим работы:'
    arg_params['mode'] = prompt_query(ACTIONS.values())
    if arg_params['mode'] == 1:
        print u'Выберете действие:'
        arg_params['scenary'] = prompt_query(REMOTE_SCENARIES.values())
        if arg_params['scenary'] == 2:
            print u'Выберете предмет поиска:'
            arg_params['dig_priorities'] = [prompt_query(REMOTE_DIGGER_PRIORITY.values())]
        elif arg_params['scenary'] == 5:
            print u'Выберете наши действия с торговцем:'
            arg_params['trader_position'] = prompt_query(REMOTE_TRADER_POSITION.values())
            print u'Выберете предмет поиска:'
            arg_params['trader_priorities'] = [prompt_query(REMOTE_TRADER_PRIORITY.values())]

    game = Game().run(site, account, arg_params)
    while True:
        pass
