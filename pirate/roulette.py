# -*- coding: utf-8 -*-

import logging
from engine.game_types import GamePlayGame, PirateEnemyHit
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class PirateRouletteBot(BaseBot):

    def perform_action(self):

        pirate_enemies = self.get_game_state().get_objects_by_types([u'pirateEnemy'])
        if pirate_enemies:
            pirate_enemy = pirate_enemies[0]

            if pirate_enemy.health:
                pirate_enemy_obj = self.get_item_reader().get(pirate_enemy.item)
                logger.info(u'Обнаружен %s. Наносим урон.' % pirate_enemy_obj.name)
                pirate_enemy_hit_event = PirateEnemyHit(objId=pirate_enemy.id)
                self.get_events_sender().send_game_events([pirate_enemy_hit_event])
                return

        roll_events = []
        buildings = self.get_game_state().get_objects_by_types([u'building'])

        for building in buildings:
            building_item = self.get_item_reader().get(building.item)
            for game in building_item.games:
                game_id = game.id
                next_play = None
                next_play_times = building.nextPlayTimes.__dict__
                if next_play_times.get(game_id):
                    next_play = int(next_play_times[game_id])

                if (next_play and self.get_timer().has_elapsed(next_play, 2)) or not len(next_play_times.keys()):

                    logger.info(u'Крутим рулетку в %s %i (%i, %i)' %
                                (building_item.name, building.id, building.x, building.y))

                    roll = GamePlayGame(building.id, game_id)
                    roll_events.append(roll)

        self.get_events_sender().send_game_pack_events(roll_events)
        self.get_events_sender().send_game_events()
