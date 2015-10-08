# -*- coding: utf-8 -*-

import logging

from engine.base import BaseBot
from engine.game_types import ChangeLocation
from engine.helpers import timestamp_to_str


logger = logging.getLogger(__name__)


class RemoteLocationBot(BaseBot):

    def __init__(self, game):
        super(RemoteLocationBot, self).__init__(game)

        self.remote_scenary = self.get_game().arg_params.get('scenary')

        # Переход к друзьям в случайном порядке
        self.random_choice = True
        self.location_id = None

    def perform_action(self):

        players = self.get_game_state().get_players()
        if players:
            friend = players[0]
        else:
            logger.info(u'Нет друзей удовлетворяющих условиям фильтра')
            self.get_game_state().set_remote_stop(True)
            self.get_params().exclude_players = []
            return

        self.location_id = self.get_game_state().get_players_location(friend.id)
        self.get_params().exclude_players.append(friend.id)

        logger.info(u'*' * 56)
        logger.info(u'Осталось: %i игроков' % len(self.get_game_state().get_players()))
        logger.info(u'Страница: vk.com/id%s\t\tИмя:    %s' %
                    (friend.id, friend.name if hasattr(friend, 'name') else u'---'))
        logger.info(u'Уровень:  %s\t\t\tОпыт:   %i' % ((u'%i   ' % friend.level)[:4], friend.exp))
        logger.info(u'Статус:   %s\t\t\tОстров: %s' %
                    (self.get_item_reader().get(friend.playerStatus).name, self.get_location_name(self.location_id)))
        if hasattr(friend, 'accessDate'):
            logger.info(u'Отсутствует: %s' % ' '.join(timestamp_to_str(abs(int(friend.accessDate)))))

        change_location_event = ChangeLocation(user=friend.id, locationId=self.location_id)
        self.send_event([change_location_event])
        self.get_game_state().set_current_user(friend)
        self.get_game_state().clear_pickups()

    def send_event(self, evt_list):
        evts = self.get_events_sender().send_game_events(evt_list)
        for evt in evts:
            if evt.type == u'gameState':
                return True
        self.send_event([])

    def get_location_name(self, location_id):
        return self.get_item_reader().get(location_id).name
