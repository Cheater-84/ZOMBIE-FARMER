# -*- coding: utf-8 -*-

import logging
from engine.game_types import MoveToStorage
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class PirateAntiChopBot(BaseBot):

    def perform_action(self):
        chops = self.get_game_state().get_objects_by_types([u'chop'])
        chops.sort(key=lambda x: x.chopCount, reverse=True)

        enemies = self.get_game_state().get_objects_by_types([u'pirateEnemy'])
        if enemies:
            chops.insert(0, enemies[0])

        chop_events = []

        for chop in chops:
            chop_obj = self.get_item_reader().get(chop.item)
            logger.info(u'Убираем на склад %s %i' % (chop_obj.name, chop.id))
            evt = MoveToStorage(objId=chop.id)
            chop_events.append(evt)
            self.get_game_state().remove_object_by_id(chop.id)

        self.get_events_sender().send_game_pack_events(chop_events)
