# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
# from engine.game_types import GameSellGameObject, BuyResource

logger = logging.getLogger(__name__)


class LocalManualBot(BaseBot):

    def __init__(self, game):
        super(LocalManualBot, self).__init__(game)

    def perform_action(self):

        if not self.get_params().switch_local_manual_bot:
            return

        # evt = BuyResource(itemId=u'CR_97', count=400L)
        # evts = self.get_events_sender().send_game_events([evt])
        # evt = BuyResource(itemId=u'CR_98', count=200L)
        # evts = self.get_events_sender().send_game_events([evt])
        # a = 0

        # Убираем все грядки
        # decor_evts = []
        # decorations = self.get_game_state().get_objects_by_types([u'plant'])
        # decorations += self.get_game_state().get_objects_by_items([u'@GROUND'])
        # for decoration in decorations:
        #     evt = GameSellGameObject(objId=decoration.id)
        #     decor_evts.append(evt)
        #     self.get_game_state().remove_object_by_id(decoration.id)
        #
        # if decor_evts:
        #     decoration_obj = self.get_item_reader().get(decoration.item)
        #     logger.info(u'Удаляем %s %i шт' % (decoration_obj.name, len(decor_evts)))
        #     self.get_events_sender().send_game_events(decor_evts)

        # Получаем карту объектов
        # {"action":"placeFromStorage","x":64,"itemId":"SC_FISHER_GRAVE_BRAINER","type":"item","y":48,"objId":6340}
