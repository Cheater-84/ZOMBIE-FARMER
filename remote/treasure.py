# -*- coding: utf-8 -*-

import logging
from remote.base import RemoteBot
from remote.steal import RemoteStealBot
from engine.game_types import GameRemoteDigItem

logger = logging.getLogger(__name__)


class RemoteTreasureBot(RemoteBot):

    def __init__(self, game):
        super(RemoteTreasureBot, self).__init__(game)

        self.stealBot = RemoteStealBot(game)

        # Главная функция
        self.action = self.remote_treasure

        # Объекты под которыми не ищем клады
        self.denied_dig_types = self.get_params().exclude_treasure_dig_types

        self.all_digged = False

    def dig_object(self, go):
        remote_dig = GameRemoteDigItem(objId=go.id, x=go.x, y=go.y)
        response_events = self.get_events_sender().send_game_events([remote_dig])

        for event in response_events:
            if event.type == u'alert':
                if event.msg == u'SERVER_TREASURE_FOUND':
                    return True
                elif event.msg == u'SERVER_REMOTE_TREASURE_ALL_DIGGED':
                    self.all_digged = True
        return False

    def remote_treasure(self, event_to_handle):

        self.all_digged = False
        remote_game_objects = event_to_handle.gameObjects

        # Крадем мешочки по ходу жизни
        self.stealBot.remote_pick(event_to_handle)

        # Не копнули ни разу
        dig_count = 0

        if event_to_handle.haveTreasure:
            # получили список объектов где будем рыть
            allow_objects = [x for x in remote_game_objects if x.type not in self.denied_dig_types]
            for go in allow_objects:
                # при переходе к следущему объекту проверяем лимит на копку
                # или что все уже выкопано
                if dig_count == 300 or self.all_digged:
                    break

                go_obj = self.get_item_reader().get(go.item)
                logger.info(u'Пробуем копать под %s %i (%i, %i)' % (go_obj.name, go.id, go.x, go.y))

                # найдено кладов
                treasure_count = 0

                # копнув, проверяем выпали ли сокровица
                found_treasure = self.dig_object(go)

                # увеличиваем счетчик найденых под объектом кладов на 1
                if found_treasure:
                    treasure_count += 1

                # увеличиваем счетчик лопат на 1
                dig_count += 1
                # если лимит на копку, выходим
                if dig_count == 300 or self.all_digged:
                    # если нашли клады но кончились лопатки показываем сколько накопали кладов
                    if treasure_count:
                        logger.info(u'Найдено %i кладов под %s %i (%i, %i)' %
                                    (treasure_count, go_obj.name, go.id, go.x, go.y))
                    break

                # если выпали сокровища роем там дальше
                while found_treasure:
                    # копнув, проверяем выпали ли сокровица
                    found_treasure = self.dig_object(go)

                    # увеличиваем счетчик найденых под объектом кладов на 1
                    if found_treasure:
                        treasure_count += 1

                    # увеличиваем счетчик лопат на 1
                    dig_count += 1
                    # если лимит на копку, выходим
                    if dig_count == 300 or self.all_digged:
                        # если нашли клады но кончились лопатки показываем сколько накопали кладов
                        if treasure_count:
                            logger.info(u'Найдено %i кладов под %s %i (%i, %i)' %
                                        (treasure_count, go_obj.name, go.id, go.x, go.y))
                        break

                # если нашли клады показываем сколько накопали кладов
                if treasure_count:
                    logger.info(u'Найдено %i кладов под %s %i (%i, %i)' %
                                (treasure_count, go_obj.name, go.id, go.x, go.y))

            if allow_objects:
                logger.info(u'Использовали %i лопат' % dig_count)
