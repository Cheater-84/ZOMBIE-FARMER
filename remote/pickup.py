# -*- coding: utf-8 -*-

import logging
from engine.game_types import GamePickPickup
from remote.base import BaseBot

logger = logging.getLogger(__name__)


class RemotePickupBot(BaseBot):

    def perform_action(self):
        pickups = self.get_game_state().get_pickups()
        if not pickups:
            return
        pickup_events = []

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
