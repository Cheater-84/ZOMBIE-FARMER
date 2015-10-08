# -*- coding: utf-8 -*-

from engine.base import Core
from tropic.roulette import TropicRouletteBot
from tropic.capture import TropicCaptureBot
from tropic.chop import TropicChopBot
from tropic.pick import TropicPickBot
from tropic.event import TropicEventHandler


class TropicCore(Core):

    def get_presets(self):

        single_bots = []

        circle_bots = [
            TropicRouletteBot(self.get_game()),
            TropicCaptureBot(self.get_game()),
            TropicPickBot(self.get_game()),
            TropicChopBot(self.get_game())
        ]
        event_handler = TropicEventHandler(self.get_game())

        return single_bots, circle_bots, event_handler
