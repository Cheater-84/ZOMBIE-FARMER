# -*- coding: utf-8 -*-

import logging
from remote.base import RemoteBot
from engine.game_types import GameRemoteFertilizeItem

logger = logging.getLogger(__name__)


class RemoteFertilizeBot(RemoteBot):

    def __init__(self, game):
        super(RemoteFertilizeBot, self).__init__(game)

        # Главная функция
        self.action = self.remote_fertilize

    # Максимум деревьев сколько можно удобрить в сутки
    max_fertilize_tree = 20

    # Количество уже удобренных деревьев
    count_fertilize_tree = 0

    # Типы фруктовых деревьев
    @staticmethod
    def get_fruit_types():
        return [u'fruitTree']

    # Определяем можно ли удобрить дерево
    def is_valid_fertilize(self, fruit_tree):
        is_valid = True
        remote_fertilize_fruits = self.get_game_state().get_state().remoteFertilizeFruitTree

        # Если дерево уже удобрено кем то
        if fruit_tree.fertilized:
            is_valid = False

        # Если дерево уже созрело
        if float(fruit_tree.jobFinishTime) < 0:
            is_valid = False

        # Если сегодня уже удобряли это дерево
        for remote_fertilize_fruit in remote_fertilize_fruits:
            if remote_fertilize_fruit.user == self.get_game_state().get_current_user().id:
                is_valid = False
                break

        return is_valid

    def remote_fertilize(self, event_to_handle):
        self.count_fertilize_tree = len(self.get_game_state().get_state().remoteFertilizeFruitTree)

        # Если суточный лимит еще не исчерпан
        if self.count_fertilize_tree < self.max_fertilize_tree:
            remote_game_objects = event_to_handle.gameObjects

            if event_to_handle.haveRemoteFertilizeFruit:
                for fruit_tree in remote_game_objects[:-1]:
                    if fruit_tree.type in self.get_fruit_types():
                        if self.is_valid_fertilize(fruit_tree):
                            fruit_tree_obj = self.get_item_reader().get(fruit_tree.item)
                            fertilize_event = GameRemoteFertilizeItem()
                            response_events = self.get_events_sender().send_game_events([fertilize_event])

                            fertilize_ok = True
                            for event in response_events:
                                if event.type == u'alert':
                                    if event.msg == u'SERVER_REMOTE_FERTILIZE_FRUIT_TREE_NOT_FOUND':
                                        logger.info(u'Дерево для удобрения не найдено')
                                        fertilize_ok = False
                                    elif event.msg == u'SERVER_REMOTE_FERTILIZE_FRUIT_TREE_NO_TRIES':
                                        logger.info(u'Уже удобрено %i деревьев' % self.max_fertilize_tree)
                                        self.get_game_state().set_remote_stop(True)
                                        return

                            if fertilize_ok:
                                logger.info(u'Удобряем %s %i' % (fruit_tree_obj.name, fruit_tree.id))
                                self.count_fertilize_tree += 1
                                break
        else:
            logger.info(u'Уже удобрено %i деревьев' % self.max_fertilize_tree)
            self.get_game_state().set_remote_stop(True)
