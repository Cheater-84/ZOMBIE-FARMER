# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import AddWishListItem

logger = logging.getLogger(__name__)


class LocalWantBot(BaseBot):

    def __init__(self, game):
        super(LocalWantBot, self).__init__(game)

    def perform_action(self):

        if not self.get_params().switch_local_want_bot:
            return

        wish_list_target = self.get_game_state().get_state().wishlist
        wish_list_source = self.get_params().wish_list

        # Если нет пустых ячеек выходим
        if None not in wish_list_target:
            return

        for index in xrange(len(wish_list_target)):
            # Если у нас пустая ячейка
            if not wish_list_target[index]:
                for wish_item_source in wish_list_source:
                    # Подбираем в хотелку то, что там еще не стоит
                    if wish_item_source not in wish_list_target:
                        wish_item_obj = self.get_item_reader().get(wish_item_source)
                        add_evt = AddWishListItem(itemId=wish_item_obj.id, index=long(index))
                        self.get_events_sender().send_game_events([add_evt])

                        logger.info(u'Поставили в хотелку %s' % wish_item_obj.name)
                        wish_list_target[index] = wish_item_source
                        break
