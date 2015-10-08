# -*- coding: utf-8 -*-

import logging
from engine.game_types import CaptureEvent
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class TropicCaptureBot(BaseBot):

    def perform_action(self):
        buildings = self.get_game_state().get_objects_by_types([u'captureObject'])

        for building in buildings:
            building_name = self.get_item_reader().get(building.item).name
            logger.info(u'Захватываем %s %i (%i, %i)' % (building_name, building.id, building.x, building.y))
            capture_event = CaptureEvent(objId=building.id)
            self.get_events_sender().send_game_events([capture_event])
