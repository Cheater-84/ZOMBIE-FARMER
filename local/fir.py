# -*- coding: utf-8 -*-

import logging
from engine.game_types import GetNewYearGift
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalFirBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_fir_bot:
            return

        events = []
        new_year_tree_list = self.get_game_state().get_objects_by_types(['newYearTree'])

        for newYearTree in new_year_tree_list:
            for gifter in newYearTree.users:
                gifter_obj = self.get_item_reader().get(gifter.gift)
                friend = self.get_game_state().get_player(gifter.id)
                user_name = friend.name if hasattr(friend, 'name') else gifter.id
                logger.info(u'Принимаем %s от %s' % (gifter_obj.name, user_name))
                new_year_gift = GetNewYearGift(objId=newYearTree.id)
                events.append(new_year_gift)
                self.get_game_state().add_storage(gifter_obj.item, gifter_obj.count)

        self.get_events_sender().send_game_pack_events(events)
