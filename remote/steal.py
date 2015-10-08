# -*- coding: utf-8 -*-

import logging
from remote.base import RemoteBot
from engine.game_types import GameRemotePickItem

logger = logging.getLogger(__name__)


class RemoteStealBot(RemoteBot):

    def __init__(self, game):
        super(RemoteStealBot, self).__init__(game)

        # Главная функция
        self.action = self.remote_pick

    def remote_pick(self, event_to_handle):

        remote_game_objects = event_to_handle.gameObjects
        on = []
        off = []

        guarded = False
        for go in remote_game_objects:
            if u'guardGrave' in go.type:
                guarded = True
                if go.started:
                    on.append(go.item)
                else:
                    off.append(go.item)

            if u'diggerGrave' in go.type:
                if go.started:
                    on.append(go.item)
                else:
                    off.append(go.item)

        if on or off:
            set_workers = set(on + off)
            for x in set_workers:
                worker_obj = self.get_item_reader().get(x)
                res_list = []
                if on.count(x):
                    res_list.append(u'%i шт работают' % on.count(x))
                if off.count(x):
                    res_list.append(u'%i шт спят' % off.count(x))
                if res_list:
                    logger.info(u'***  %s: %s' % (worker_obj.name, u', '.join(res_list)))

        if not guarded:
            items = [x for x in remote_game_objects if x.type in u'pickup']
            for go in items:
                go_obj = self.get_item_reader().get(go.item)
                if not (hasattr(go_obj, u'openOnlyByOwner') and go_obj.openOnlyByOwner):
                    pick_event = GameRemotePickItem(objId=go.id)
                    response_events = self.get_events_sender().send_game_events([pick_event])

                    if u'alert' not in [x.type for x in response_events]:
                        logger.info(u'Открываем %s %i (%i, %i)' % (go_obj.name, go.id, go.x, go.y))

            for go in remote_game_objects:
                if u'diggerGrave' in go.type and go.materials:
                    pick_event = GameRemotePickItem(objId=go.id)
                    response_events = self.get_events_sender().send_game_events([pick_event])

                    if u'alert' not in [x.type for x in response_events]:
                        worker = self.get_item_reader().get(go.item).name
                        logger.info(u'Открываем ведро у %s %i' % (worker, go.id))

                    go.materials -= 1
