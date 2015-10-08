# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class PirateEventHandler(BaseBot):

    def __init__(self, game):
        super(PirateEventHandler, self).__init__(game)

        self.event_actions = {
            'pirateCapture': self.pirate_capture_event,
            'exploration': self.exploration_event,
            'game': self.game_event,
            'pirateEnemy': self.enemy_hit_event,
            'pickup': self.pickup_event
        }

    def event_handle(self):

        for event in self.get_events_sender().get_game_events():
            action = self.event_actions.get(event.type)
            if action:
                action(event)

            self.get_events_sender().remove_game_event(event)

    def pirate_capture_event(self, event):
        go = self.get_game_state().get_object_by_id(event.objId)
        go_obj = self.get_item_reader().get(go.item)

        if event.action == u'captured' and not go.captured:
            if hasattr(event, 'user'):
                logger.info(u'%s уже захвачен другом %s' % (go_obj.name, event.user))
            else:
                logger.info(u'%s захвачен нами' % go_obj.name)
            go.captured = True

    def exploration_event(self, event):
        if event.gameObjects:
            self.get_game_state().get_state().gameObjects += event.gameObjects

    def game_event(self, event):
        go = self.get_game_state().get_object_by_id(event.objId)

        if not go:
            return

        go.nextPlayTimes.__setattr__(event.extraId, event.nextPlayDate)
        building = self.get_item_reader().get(go.item)
        for game in building.games:
            prize_pos = event.result.pos
            game_prize = game.prizes[prize_pos]
            prize = self.get_item_reader().get(game_prize.item)
            logger.info(u'Вы выиграли %s %i шт' % (prize.name, game_prize.count))

            instruments = self.get_game_state().get_state().pirate.instruments
            for instrument in instruments:
                if instrument.item in game_prize.item:
                    instrument.count += game_prize.count
                    break

    def enemy_hit_event(self, event):

        if event.action == u'hitted':
            go = self.get_game_state().get_object_by_id(event.objId)

            if not go:
                return

            go.health = event.health
            if not event.health:
                self.get_game_state().remove_object_by_id(event.objId)

            pirate_enemy_obj = self.get_item_reader().get(go.item)
            logger.info(u'%s атакован. Осталось здоровья %i ед.' % pirate_enemy_obj.name, event.health)

    def pickup_event(self, event):
        if event.action == u'add' and event.pickups:
            self.get_game_state().add_pickups(event.pickups)
