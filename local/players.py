# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import GameGetInfo

logger = logging.getLogger(__name__)


class LocalPlayersBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_players_bot:
            return

        logger.info(u'Запрашиваем список соседей')
        friends = [unicode(x) for x in self.get_api().friends.getAppUsers()]

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
