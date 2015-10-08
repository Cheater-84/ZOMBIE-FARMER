# -*- coding: utf-8 -*-

import logging
from engine.game_types import GamePlayGame
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class TropicRouletteBot(BaseBot):

    def perform_action(self):

        roll_events = []
        buildings = self.get_game_state().get_objects_by_types([u'building'])

        for building in buildings:
            if building.item in [u'@B_AIM', u'@B_PASS_4', u'@B_PASS_3', u'@B_PASS_2', u'@B_PASS_1']:
                continue
            building_item = self.get_item_reader().get(building.item)
            if hasattr(building_item, 'upgrades'):
                if building.level < len(building_item.upgrades):
                    continue

            if hasattr(building, 'playsCounts') and building_item.games:
                if getattr(building.playsCounts, building_item.games[0].id, 0) >= 200:
                    continue

            for game in building_item.games:
                game_id = game.id
                next_play = None
                next_play_times = building.nextPlayTimes.__dict__
                if next_play_times.get(game_id):
                    next_play = int(next_play_times[game_id])

                if (next_play and self.get_timer().has_elapsed(next_play, 1)) or not len(next_play_times.keys()):

                    logger.info(u'Крутим рулетку в %s %i (%i, %i)' %
                                (building_item.name, building.id, building.x, building.y))

                    roll = GamePlayGame(building.id, game_id)
                    roll_events.append(roll)

        self.get_events_sender().send_game_pack_events(roll_events)
        self.get_events_sender().send_game_events()
