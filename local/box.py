# -*- coding: utf-8 -*-

import logging
from engine.game_types import GamePickItem, GamePickup
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalBoxBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_box_bot:
            return

        box_events = []

        boxes = self.get_game_state().get_objects_by_types([GamePickup.type])
        for box in boxes:

            box_obj = self.get_item_reader().get(box.item)
            if hasattr(box_obj, 'openingPrice') and box_obj.openingPrice:
                continue
            logger.info(u'Открываем %s %i (%i, %i)' % (box_obj.name, box.id, box.x, box.y))
            pick_event = GamePickItem(objId=box.id)
            box_events.append(pick_event)
            self.get_game_state().remove_object_by_id(box.id)

        self.get_events_sender().send_game_pack_events(box_events)
