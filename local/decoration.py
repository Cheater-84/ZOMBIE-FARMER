# -*- coding: utf-8 -*-

import logging
from engine.game_types import MoveToStorage
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalDecorationBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_decoration_bot:
            return

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
