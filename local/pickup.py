# -*- coding: utf-8 -*-

import logging
from engine.game_types import GamePickPickup
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalPickupBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_pickup_bot:
            return

        pickups = self.get_game_state().get_pickups()
        if not pickups:
            return
        pickup_events = []

        if len(pickups) > 1000:
            logger.info(u'Подбираем выпавшие предметы, %i шт...' % len(pickups))

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
