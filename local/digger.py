# -*- coding: utf-8 -*-
import logging
from engine.game_types import GameDiggerGrave, GameDiggerGraveWithBrains, StartWorker, GamePickItem
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalDiggerBot(BaseBot):

    @staticmethod
    def get_worker_types():
        return [GameDiggerGrave.type, GameDiggerGraveWithBrains.type]

    def perform_action(self):

        if not self.get_params().switch_local_digger_bot:
            return

        grave_evts = []

        graves = self.get_game_state().get_objects_by_types(self.get_worker_types())
        for grave in graves:
            grave_obj = self.get_item_reader().get(grave.item)
            if not grave.started:
                start_evt = StartWorker(objId=grave.id)
                evts = self.get_events_sender().send_game_events([start_evt])

                # Если от сервера пришло сообщение о том что нет мозгов,
                # то обрабатываем его сразу чтобы знать кто не будет работать
                no_brains = False
                for evt in evts:
                    if evt.type == u'alert':
                        if evt.msg == u'SERVER_NO_BRAINS':
                            no_brains = True
                if not no_brains:
                    logger.info(u'Отправляем %s %i работать' % (grave_obj.name, grave.id))
                    grave.started = True

            if grave.materials:
                logger.info(u'Собираем мешки у %s %i %i шт' % (grave_obj.name, grave.id, grave.materials))
                while grave.materials:
                    pick_item = GamePickItem(itemId=None, objId=grave.id)
                    grave_evts.append(pick_item)
                    grave.materials -= 1

        self.get_events_sender().send_game_pack_events(grave_evts)
