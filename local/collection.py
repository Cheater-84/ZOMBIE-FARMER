# -*- coding: utf-8 -*-

import logging
from engine.game_types import GameExchangeCollection
from engine.base import BaseBot
from engine.helpers import get_item_count

logger = logging.getLogger(__name__)


class LocalCollectionBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_collection_bot:
            return

        changed_colls = self.get_params().changed_colls

        for coll in changed_colls:
            coll_obj = self.get_item_reader().get(coll.name)
            coll_count = self.get_game_state().count_collection(coll_obj.items)
            delta = get_item_count(coll, coll_count)

            if delta:
                logger.info(u'Обменяли %s %i шт' % (coll_obj.name, delta))
                exchange_coll_event = GameExchangeCollection(itemId=coll.name, count=delta)
                self.get_events_sender().send_game_events([exchange_coll_event])
                self.get_game_state().remove_collection(coll_obj.items, delta)

                for prize in coll_obj.prizes:
                    if prize.item == u'@COINS':
                        self.get_game_state().get_state().gameMoney += prize.count * delta
                    elif prize.item == u'@XP':
                        self.get_game_state().get_state().experience += prize.count * delta
                    elif prize.item == u'@CASH':
                        self.get_game_state().get_state().cashMoney += prize.count * delta
                    else:
                        self.get_game_state().add_storage(prize.item, prize.count * delta)
