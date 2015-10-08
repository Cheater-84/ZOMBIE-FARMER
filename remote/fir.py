# -*- coding: utf-8 -*-

import logging
from remote.base import RemoteBot
from engine.game_types import GameRemoteGiftItem

logger = logging.getLogger(__name__)


class RemoteNewYearTreeBot(RemoteBot):

    def __init__(self, game):
        super(RemoteNewYearTreeBot, self).__init__(game)

        # Главная функция
        self.action = self.remote_tree

        # Максимум сколько Я кладу подарков ОДНОМУ другу
        self.my_limit_tree = self.get_params().fir_limit

    # Максимум пряников сколько можно положить в сутки
    max_new_year_tree = 150

    # Количество уже подаренных пряников
    count_new_year_tree = 0

    # Типы елочки
    @staticmethod
    def get_tree_types():
        return [u'newYearTree']

    # Виды елочек
    @staticmethod
    def get_tree_items():
        return [u'@B_SPRUCE_MIDDLE', u'@B_SPRUCE_BIG', u'@B_SPRUCE_SMOLL']

    # Определяем можно ли положить пряник под елку
    def is_valid_tree_item(self, tree_item):
        is_valid = True
        remote_new_years = self.get_game_state().get_state().remoteNewYear

        # Если найденный объект не ёлка
        if tree_item.item not in self.get_tree_items():
            is_valid = False

        # Если елка еще не достроена
        if tree_item.level < 2L:
            is_valid = False

        # Если в маленькую елку уже положили 3 пряника
        if tree_item.item == u'@B_SPRUCE_SMOLL' and len(tree_item.users) == 3:
            is_valid = False

        # Если в большую елку уже положили 6 пряников
        if tree_item.item == u'@B_SPRUCE_MIDDLE' and len(tree_item.users) == 6:
            is_valid = False

        # Если в огромную елку уже положили 15 пряников
        if tree_item.item == u'@B_SPRUCE_BIG' and len(tree_item.users) == 15:
            is_valid = False

        # Если не забрали пряник из под елки
        for user in tree_item.users:
            if user.id == self.get_game_state().get_current_user().id:
                is_valid = False
                break

        # Если забрали пряник, но мы сегодня уже дарили
        for remote_new_year in remote_new_years:
            if remote_new_year.treeId == tree_item.id:
                is_valid = False
                break

        return is_valid

    def remote_tree(self, event_to_handle):
        self.count_new_year_tree = len(self.get_game_state().get_state().remoteNewYear)

        remote_game_objects = event_to_handle.gameObjects

        count_tree = 0
        for remote_object in remote_game_objects:
            # Если суточный лимит еще не исчерпан
            if self.count_new_year_tree < self.max_new_year_tree:
                # Если нашли елочку
                if remote_object.type in self.get_tree_types() and remote_object.item in self.get_tree_items():
                    new_year_tree = remote_object

                    # Если она не удовлетворяет условиям, то ищем следующую
                    if not self.is_valid_tree_item(new_year_tree):
                        continue

                    remote_new_year_item = GameRemoteGiftItem(objId=new_year_tree.id)
                    response_events = self.get_events_sender().send_game_events([remote_new_year_item])

                    send_ok = True
                    for event in response_events:
                        if event.type == u'alert':
                            if event.msg == u'SERVER_NEW_YEAR_GIFT_NOT_ALLOW':
                                send_ok = False

                    if send_ok:
                        self.count_new_year_tree += 1
                        count_tree += 1

                # Если уже достаточно настучали одному товарищу
                if self.my_limit_tree and count_tree >= self.my_limit_tree:
                    break
            # Если уже выбрали лимит на сутки
            else:
                logger.info(u'Кладем под елочки %i пряников' % count_tree)
                logger.info(u'Уже подарено %i пряников' % self.max_new_year_tree)
                self.get_game_state().set_remote_stop(True)
                return

        logger.info(u'Кладем под елочки %i пряников' % count_tree)
