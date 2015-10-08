# -*- coding: utf-8 -*-

from engine.base import Core
from pirate.roulette import PirateRouletteBot
from pirate.capture import PirateCaptureBot
from pirate.chop import PirateChopBot
from pirate.antichop import PirateAntiChopBot
from pirate.pick import PiratePickBot
from pirate.event import PirateEventHandler


class PirateCore(Core):

    def get_presets(self):

        single_bots = []

        circle_bots = [
            PirateRouletteBot(self.get_game()),
            PirateCaptureBot(self.get_game()),
            PiratePickBot(self.get_game()),
            PirateChopBot(self.get_game())
        ]
        event_handler = PirateEventHandler(self.get_game())

        return single_bots, circle_bots, event_handler
