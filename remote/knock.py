# -*- coding: utf-8 -*-

import logging
from remote.base import RemoteBot
from engine.game_types import GameRemoteHalloweenPumpkin

logger = logging.getLogger(__name__)


class RemoteKnockBot(RemoteBot):

    def __init__(self, game):
        super(RemoteKnockBot, self).__init__(game)

        # Главная функция
        self.action = self.remote_halloween

    # Максимум сколько можно в тыкву стукнуть
    max_pumpkin = 200

    # Количество стуков в тыкву
    count_pumpkin = 200

    # Типы тыквы
    @staticmethod
    def get_halloween_types():
        return [u'halloweenTower']

    @staticmethod
    def get_halloween_items():
        return [u'@B_BIG_PUMPKIN', u'@B_PUMPKIN_PYRAMIDE']

    # Проверяем можно ли в тыкву стукнуть
    def is_valid_pumpkin_item(self, pumpkin):
        is_valid = True
        remote_trick_treating = self.get_game_state().get_state().remoteTrickTreating

        # Если не забрали тыкву
        for user in pumpkin.users:
            if user.id == self.get_game_state().get_current_user().id:
                is_valid = False
                break

        # Если сегодня уже удобрили это дерево
        for remote_trick in remote_trick_treating:
            if remote_trick.user == self.get_game_state().get_current_user().id:
                is_valid = False
                break

        return is_valid

    def remote_halloween(self, event_to_handle):
        self.count_pumpkin = len(self.get_game_state().get_state().remoteTrickTreating)

        if self.count_pumpkin < self.max_pumpkin:
            remote_game_objects = event_to_handle.gameObjects
            success_items = []

            item_ids = {
                u'@B_PUMPKIN_PYRAMIDE': u'KITTY_PACK_DEFAULT',
                u'@B_BIG_PUMPKIN': u'PUMPKIN_PACK_DEFAULT'
            }

            for remote_object in remote_game_objects:
                # Если нашли стуковую постройку
                if remote_object.type in self.get_halloween_types() and remote_object.item in self.get_halloween_items() and \
                        remote_object.item not in success_items:
                    remote_pumpkin = remote_object

                    # Если она не удовлетворяет условиям, то ищем следующую
                    if not self.is_valid_pumpkin_item(remote_pumpkin):
                        continue

                    logger.info(u'Стучим в %s %i' %
                                (self.get_item_reader().get(remote_pumpkin.item).name, remote_pumpkin.id))

                    remote_pumpkin_item = GameRemoteHalloweenPumpkin(objId=remote_pumpkin.id,
                                                                     itemId=item_ids[remote_pumpkin.item])

                    self.get_events_sender().send_game_events([remote_pumpkin_item])

                    # Добавляем тип постройки в которую уже стукнули
                    success_items.append(remote_pumpkin.item)
        else:
            logger.info(u'Уже стукнуто в %i тыкв' % self.max_pumpkin)
