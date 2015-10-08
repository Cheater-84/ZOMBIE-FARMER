# -*- coding: utf-8 -*-

import logging
from engine.game_types import PaintballTargetTransform, GameRemotePickItem
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalKnockingBot(BaseBot):

    def __init__(self, game):
        super(LocalKnockingBot, self).__init__(game)

        self.target_types = [u'@B_PAINTBALL_TARGET1', u'@B_PAINTBALL_TARGET2', u'@B_PAINTBALL_TARGET3']

    def perform_action(self):

        if not self.get_params().switch_local_knock_bot:
            return

        targets = self.get_game_state().get_objects_by_items(self.target_types)
        if targets:

            target_events = []
            for target in targets:
                target_obj = self.get_item_reader().get(target.item)
                if target.transformPlaysCount == target_obj.transformPlaysCount:
                    target_transform = PaintballTargetTransform(objId=target.id, itemId=target_obj.id)
                    target_pick = GameRemotePickItem(objId=target.id)
                    # target_rebuy = GameBuyItem(objId=target.id, itemId=target_obj.id, x=target.x, y=target.y)

                    target_events.append(target_transform)
                    target_events.append(target_pick)
                    # target_events.append(target_rebuy)

                    logger.info(u'Превращаем и ставим заново %s %i (%i, %i)' %
                                (target_obj.name, target.id, target.x, target.y))

                    self.get_game_state().get_state().gameMoney -= target_obj.buyCoins

            self.get_events_sender().send_game_pack_events(target_events)
