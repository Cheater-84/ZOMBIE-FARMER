# -*- coding: utf-8 -*-
import logging
from engine.game_types import GameRemotePickItem, MonsterDig
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalMonsterBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_monster_bot:
            return

        monsters = self.get_game_state().get_objects_by_types(['monsterPit'])
        if not monsters:
            return

        monster = monsters[0]

        if monster.state == u'HAVE_PICKUP_BOX':
            monster_obj = self.get_item_reader().get(monster.item)
            pick_evt = GameRemotePickItem(objId=monster.id)

            logger.info(u'Забираем сундук у %s' % monster_obj.name)
            self.get_events_sender().send_game_events([pick_evt])

        if monster.state == u'READY_FOR_DIG':
            monster_obj = self.get_item_reader().get(monster.item)
            dig_evt = MonsterDig(objId=monster.id)
            logger.info(u'Закапываем %s' % monster_obj.name)
            self.get_events_sender().send_game_events([dig_evt])
