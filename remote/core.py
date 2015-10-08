# -*- coding: utf-8 -*-

from engine.base import Core
from remote.location import RemoteLocationBot
from remote.fir import RemoteNewYearTreeBot
from remote.digger import RemoteDiggerBot
from remote.steal import RemoteStealBot
from remote.treasure import RemoteTreasureBot
from remote.knock import RemoteKnockBot
from remote.trader import RemoteTraderBot
from remote.fertilize import RemoteFertilizeBot
from remote.players import RemotePlayersBot
from remote.event import RemoteEventHandler


class RemoteCore(Core):

    def __init__(self, game):
        super(RemoteCore, self).__init__(game)

        self.remote_scenary = self.get_game().arg_params.get('scenary')

    def get_presets(self):
        single_bots = [
            RemotePlayersBot(self.get_game())
        ]

        actions = {
            0: RemoteNewYearTreeBot(self.get_game()),
            1: RemoteFertilizeBot(self.get_game()),
            2: RemoteDiggerBot(self.get_game()),
            3: RemoteStealBot(self.get_game()),
            4: RemoteTreasureBot(self.get_game()),
            5: RemoteTraderBot(self.get_game()),
            6: RemoteKnockBot(self.get_game())
        }

        event_handler = RemoteEventHandler(self.get_game())

        circle_bots = [
            RemoteLocationBot(self.get_game())
        ]
        circle_bots.insert(1, actions.get(self.remote_scenary))

        return single_bots, circle_bots, event_handler

    def get_stop_condition(self):
        return self.get_game().game_state.get_remote_stop()
