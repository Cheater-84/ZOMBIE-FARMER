# -*- coding: utf-8 -*-

import logging
from engine.game_types import GameSellItem, GameUseStorageItem, MoveToStorage
from engine.base import BaseBot
from engine.helpers import get_item_count

logger = logging.getLogger(__name__)


class LocalStorageBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_storage_bot:
            return

        sell_items = self.get_params().sell_items

        for sell_item in sell_items:
            item_count = self.get_game_state().count_storage(sell_item.name)
            delta = get_item_count(sell_item, item_count)
            if delta:
                item_obj = self.get_item_reader().get(sell_item.name)

                sell_item_event = GameSellItem(itemId=sell_item.name[1:], count=delta)
                self.get_events_sender().send_game_events([sell_item_event])
                self.get_game_state().remove_storage(sell_item.name, delta)

                logger.info(u'Продали со склада %s %i шт' % (item_obj.name, delta))

        for wealth in self.get_params().wealth_types:
            wealth_count = self.get_game_state().count_storage(wealth)
            item_obj = self.get_item_reader().get(wealth)

            if wealth_count:
                logger.info(u'Открываем со склада %s %i шт' % (item_obj.name, wealth_count))

                while wealth_count:
                    x = 10 if wealth_count >= 10 else wealth_count
                    wealth_event = GameUseStorageItem(itemId=item_obj.id, x=10, y=10)
                    self.get_events_sender().send_game_events([wealth_event] * x)
                    self.get_game_state().remove_storage(wealth, x)
                    wealth_count -= x

        # Если на текущем острове нельзя убирать декор то выходим
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in self.get_params().allow_move_decoration_locations:
            decor_evts = []
            decorations = self.get_game_state().get_objects_by_types(["decoration"])
            decorations += self.get_game_state().get_objects_by_items([u'@SC_BASE', u'@SCASTLE_GIRL',
                                                                       u'@MP_MONSTER_PIT_1'])
            for decoration in decorations:
                decoration_obj = self.get_item_reader().get(decoration.item)
                logger.info(u'Убираем на склад декорацию %s' % decoration_obj.name)
                evt = MoveToStorage(objId=decoration.id)
                decor_evts.append(evt)

            if decor_evts:
                self.get_events_sender().send_game_events(decor_evts)
