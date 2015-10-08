# -*- coding: utf-8 -*-

import logging
import random
from remote.base import RemoteBot
from remote.steal import RemoteStealBot
from engine.game_types import GameRemoteDigItem

logger = logging.getLogger(__name__)


class RemoteDiggerBot(RemoteBot):

    def __init__(self, game):
        super(RemoteDiggerBot, self).__init__(game)

        self.stealBot = RemoteStealBot(game)

        # Главная функция
        self.action = self.remote_dig

        # Приоритеты для выкапывания
        self.dig_priorities = self.get_game().arg_params.get('dig_priorities')

        # Копать только под достроенной постройкой
        self.only_build_complete = False

    def remote_dig(self, event_to_handle):

        # Крадем мешочки по ходу жизни
        self.stealBot.remote_pick(event_to_handle)

        remote_game_objects = event_to_handle.gameObjects

        if event_to_handle.haveTreasure:
            target_dict = {}
            success = False

            finded = []

            for go in remote_game_objects:
                for target in self.dig_priorities:
                    if go.item in self.get_params().dig_items.get(target):
                        # Если это постройка, то он должен быть построен(опция)
                        if u'building' in go.type and self.only_build_complete:
                            if go.level < len(self.get_item_reader().get(go.item).upgrades):
                                continue
                        res = target_dict.get(target, [])
                        res.append(go)
                        target_dict[target] = res
                        success = True

                        name = self.get_item_reader().get(go.item).name
                        finded.append(name)
                        break

            if success:
                logger.info(u'Найдено: %s' % u', '.join(finded))
                for priority in self.dig_priorities:
                    dig_objects = target_dict.get(priority)
                    if dig_objects:
                        shovel_storage_count = self.get_game_state().count_storage(u'@SHOVEL_EXTRA')
                        shovel = 300 if shovel_storage_count >= 300 else shovel_storage_count
                        if not shovel:
                            logger.info(u'Закончились супер-лопаты на складе')
                            self.get_game_state().set_remote_stop(True)
                            return
                        go = random.choice(dig_objects)
                        name = self.get_item_reader().get(go.item).name
                        evts = []
                        logger.info(u'Пробуем копать под %s' % name)
                        while shovel > 0:
                            dig_event = GameRemoteDigItem(objId=go.id, x=go.x, y=go.y)
                            response_events = self.get_events_sender().send_game_events([dig_event])
                            response_events += self.get_events_sender().send_game_events([dig_event] * 9)
                            shovel -= 10

                            evts = [x for x in response_events
                                    if x.type == u'alert' and x.msg == u'SERVER_REMOTE_TREASURE_ALL_DIGGED']

                            for alert_evt in evts:
                                self.get_events_sender().remove_game_event(alert_evt)

                            if evts:
                                break

                        if evts:
                            response_events = self.get_events_sender().send_game_events()
                            evts += [x for x in response_events
                                     if x.type == u'alert' and x.msg == u'SERVER_REMOTE_TREASURE_ALL_DIGGED']

                            for alert_evt in evts:
                                self.get_events_sender().remove_game_event(alert_evt)

                            logger.info(u'Использовано %i лопат' % (300 - shovel - len(evts)))
                            return

                        logger.info(u'Использовано %i лопат' % 300)
                        return
        else:
            logger.info(u'У игрока уже все выкопано')