# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class TropicEventHandler(BaseBot):

    def __init__(self, game):
        super(TropicEventHandler, self).__init__(game)

        self.event_actions = {
            'exploration': self.exploration_event,
            'pickup': self.pickup_event,
            'game': self.game_event,
            'captureObject': self.capture_event
        }

    def event_handle(self):

        for event in self.get_events_sender().get_game_events():
            action = self.event_actions.get(event.type)
            if action:
                action(event)

            self.get_events_sender().remove_game_event(event)

    def capture_event(self, event):
        if event.action == u'captured' and not event.captured:
            self.get_game_state().remove_object_by_id(event.objId)

    def exploration_event(self, event):
        if event.gameObjects:
            self.get_game_state().get_state().gameObjects += event.gameObjects

    def pickup_event(self, event):
        pass

    def game_event(self, event):
        gameObject = self.get_game_state().get_object_by_id(event.objId)

        if not gameObject:
            return

        gameObject.nextPlayTimes.__setattr__(event.extraId, event.nextPlayDate)
        playCount = getattr(gameObject.playsCounts, event.extraId, 0)
        gameObject.playsCounts.__setattr__(event.extraId, playCount + 1)
        building = self.get_item_reader().get(gameObject.item)
        for game in building.games:
            prize_pos = event.result.pos
            game_prize = game.prizes[prize_pos]
            prize = self.get_item_reader().get(game_prize.item)
            logger.info(u'Вы выиграли %s %i шт' % (prize.name, game_prize.count))

            self.get_game_state().add_storage(game_prize.item, game_prize.count)