# -*- coding: utf-8 -*-

import logging
from engine.game_types import GameRemotePickItem, GamePickPickup
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class TropicPickBot(BaseBot):

    def perform_action(self):
        items = self.get_game_state().get_objects_by_types([u'pickup'])

        pick_events = []

        for item in items:
            item_name = self.get_item_reader().get(item.item).name
            logger.info(u'Подбираем %s %i (%i, %i)' % (item_name, item.id, item.x, item.y))
            pick_event = GameRemotePickItem(objId=item.id)
            pick_events.append(pick_event)
            self.get_game_state().remove_object_by_id(item.id)

        self.get_events_sender().send_game_pack_events(pick_events)

        pickups = self.get_game_state().get_pickups()
        if not pickups:
            return
        pickup_events = []

        if len(pickup_events) > 1000:
            logger.info(u'Подбираем выпавшие предметы...')

        for pickup in pickups:
            if pickup.type == u'coins':
                self.get_game_state().get_state().gameMoney += pickup.count
            elif pickup.type == u'xp':
                self.get_game_state().get_state().experience += pickup.count
            elif pickup.type == u'collection':
                self.get_game_state().add_collection_item(pickup.id, pickup.count)
            else:
                self.get_game_state().add_storage(pickup.id, pickup.count)

            pick_event = GamePickPickup([pickup])
            pickup_events.append(pick_event)
            self.get_game_state().remove_pickup(pickup)

        self.get_events_sender().send_game_pack_events(pickup_events)
