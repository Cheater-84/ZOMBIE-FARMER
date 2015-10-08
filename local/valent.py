# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import GameApplyCompGiftItem, GameRemotePickItem

logger = logging.getLogger(__name__)


class LocalValentBot(BaseBot):

    def __init__(self, game):
        super(LocalValentBot, self).__init__(game)

        self.max_objId = 0L

    def perform_action(self):

        if not self.get_params().switch_local_valent_bot:
            return

        # Если тот остров
        current_loc_id = self.get_game_state().get_game_loc().id

        for valent_item in self.get_params().valent_gifts:
            if current_loc_id == valent_item.location:

                gifts_events = []
                gifts = self.get_game_state().get_state().gifts

                limit = 0

                for gift in gifts:
                    if gift.item == valent_item.item:
                        gift_item = self.get_item_reader().get(gift.item)
                        friend = self.get_game_state().get_player(gift.user)
                        user_name = friend.name if hasattr(friend, 'name') else gift.user

                        # Находим максимальный objId
                        if not self.max_objId:
                            for go in self.get_game_state().get_state().gameObjects:
                                if go.id > self.max_objId:
                                    self.max_objId = long(go.id)

                        x = gift.count
                        while x:
                            self.max_objId += 1
                            apply_gift_evt = GameApplyCompGiftItem(objId=self.max_objId, itemId=gift_item.id,
                                                                   extraId=gift.id, x=valent_item.x, y=valent_item.y)
                            pick_evt = GameRemotePickItem(objId=self.max_objId)

                            gifts_events.append(apply_gift_evt)
                            gifts_events.append(pick_evt)

                            x -= 1
                            limit += 1

                        logger.info(u'Открываем %s %i шт от %s' % (gift_item.name, gift.count, user_name))
                        gifts.remove(gift)

                self.get_events_sender().send_game_pack_events(gifts_events)
