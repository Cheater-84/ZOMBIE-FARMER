# -*- coding: utf-8 -*-

import logging
import random
from base import RemoteBot
from engine.game_types import GameGetInfo

logger = logging.getLogger(__name__)


class RemotePlayersBot(RemoteBot):

    def __init__(self, game):
        super(RemotePlayersBot, self).__init__(game)

        self.remote_scenary = self.get_game().arg_params.get('scenary')
        self.stolen_island = self.get_params().stolen_island

    def perform_action(self):

        if self.get_game_state().get_players():
            return

        logger.info(u'Запрашиваем список соседей')
        friends_list = [unicode(x) for x in self.get_api().friends.getAppUsers()]

        if self.remote_scenary in [0, 1]:
            premium_accounts = self.get_params().premium_accounts
            premium_accounts.reverse()
            for premium_account in premium_accounts:
                if premium_account in friends_list:
                    index = friends_list.index(premium_account)
                    friends_list.pop(index)
                    friends_list.insert(0, premium_account)

            friends = self.get_friends({u'main': friends_list})

        elif self.remote_scenary == 2:
            if self.get_statistic().table_ready:
                if 0 in self.get_game().arg_params.get('dig_priorities'):
                    logger.info(u'Применяем фильтр по списку "Японская коллекция"')
                    friends = self.get_friends(self.get_statistic().get_user_dict(u'JAPAN'))
                elif 14 in self.get_game().arg_params.get('dig_priorities'):
                    logger.info(u'Применяем фильтр по списку "Правая половинка сердца"')
                    friends = self.get_friends(self.get_statistic().get_user_dict(u'VALRIGHT'))
                elif 15 in self.get_game().arg_params.get('dig_priorities'):
                    logger.info(u'Применяем фильтр по списку "Бозон Хиггса"')
                    friends = self.get_friends(self.get_statistic().get_user_dict(u'PLATFORM'))
                else:
                    friends = self.get_friends({u'main': friends_list})
            else:
                friends = self.get_friends({u'main': friends_list})

        elif self.remote_scenary == 3:
            logger.info(u'Применяем фильтр по списку "Свободные рыбаки и кладоискатели"')
            if self.get_statistic().table_ready:
                friends = self.get_friends(self.get_statistic().get_user_island(self.stolen_island, u'FISHER'))
            else:
                friends = self.get_friends({u'main': friends_list})
        elif self.remote_scenary == 4:
            friends = self.get_friends({self.get_params().treasure_location: friends_list})
        elif self.remote_scenary == 5:
            friends = self.get_friends({u'main': friends_list})
        else:
            friends = self.get_friends({u'main': friends_list})

        if self.get_params().exclude_players:
            logger.info(u'Исключаем уже пройденных %i соседей' % len(self.get_params().exclude_players))
            friends = [x for x in friends if x not in self.get_params().exclude_players]

        logger.info(u'Получаем данные по %i соседям' % len(friends))
        while friends:
            get_info = GameGetInfo(friends[:100])
            self.send_event([get_info])
            friends = friends[100:]

    def send_event(self, evt_list):
        evts = self.get_events_sender().send_game_events(evt_list)
        for evt in evts:
            if evt.type == u'playersInfo':
                return True
        self.send_event([])

    @staticmethod
    def format_list(user_dict):
        res = {}
        for location in user_dict:
            for user in user_dict[location]:
                res[user] = location
        return res

    def get_friends(self, user_list):
        res = self.format_list(user_list)
        self.get_game_state().set_players_location(res)

        friends = res.keys()
        return friends

    @staticmethod
    def get_offset(friends):

        total = len(friends)
        block = 100
        offset = (random.randint(1, len(friends[::block])) - 1) * block
        friends = friends[offset:offset + block]
        logger.info(u'Всего %i игроков. Смещение по списку %i. Партия %i' % (total, offset, block))
        return friends
