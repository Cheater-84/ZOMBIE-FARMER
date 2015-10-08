# -*- coding: utf-8 -*-

import logging
from engine.game_types import PirateCaptureEvent
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class PirateCaptureBot(BaseBot):

    def perform_action(self):
        buildings = self.get_game_state().get_objects_by_types([u'pirateCaptureObject'])

        for building in buildings:
            if not building.captured:
                building_name = self.get_item_reader().get(building.item).name
                logger.info(u'Захватываем %s %i (%i, %i)' % (building_name, building.id, building.x, building.y))
                capture_event = PirateCaptureEvent(objId=building.id)
                self.get_events_sender().send_game_events([capture_event])

    def event_handle(self, event_to_handle):
        go = self.get_game_state().get_object_by_id(event_to_handle.objId)
        go_name = self.get_item_reader().get(go.item).name

        if event_to_handle.action == u'captured' and not go.captured:
            if hasattr(event_to_handle, 'user'):
                logger.info(u'%s уже захвачен другом %s' % (go_name, event_to_handle.user))
            else:
                logger.info(u'%s захвачен нами' % go_name)
            go.captured = True
