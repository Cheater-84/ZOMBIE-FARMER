# -*- coding: utf-8 -*-

from engine.base import Core
from local.location import LocalLocationBot
from local.gift import LocalGiftBot
from local.collection import LocalCollectionBot
from local.storage import LocalStorageBot
from local.roulette import LocalRouletteBot
from local.fir import LocalFirBot
from local.plant import LocalPlantBot
from local.craft import LocalCraftBot
from local.pickup import LocalPickupBot
from local.box import LocalBoxBot
from local.daily import LocalDailyBot
from local.brain import LocalBrainBot
from local.cook import LocalCookBot
from local.digger import LocalDiggerBot
from local.resource import LocalResourceBot
from local.buff import LocalBuffBot
from local.builder import LocalBuilderBot
from local.send import LocalSendBot
from local.trader import LocalTraderBot
from local.magic import LocalMagicBot
from local.players import LocalPlayersBot
from local.blackjack import LocalBlackJackBot
from local.buy import LocalBuyBot
from local.valent import LocalValentBot
from local.knock import LocalKnockingBot
from local.monster import LocalMonsterBot
from local.manual import LocalManualBot
from local.want import LocalWantBot
from local.decoration import LocalDecorationBot
from local.mission import LocalMissionBot
from local.place import LocalPlaceBot
from local.event import LocalEventHandler


class LocalCore(Core):

    def get_presets(self):

        single_bots = [
            LocalManualBot(self.get_game()),
            LocalMissionBot(self.get_game()),
            LocalPlayersBot(self.get_game())
        ]

        circle_bots = [
            LocalPlaceBot(self.get_game()),
            LocalWantBot(self.get_game()),
            LocalDailyBot(self.get_game()),
            LocalMissionBot(self.get_game()),
            LocalBrainBot(self.get_game()),
            LocalValentBot(self.get_game()),
            LocalKnockingBot(self.get_game()),
            LocalGiftBot(self.get_game()),
            LocalFirBot(self.get_game()),
            LocalBoxBot(self.get_game()),
            LocalMonsterBot(self.get_game()),
            LocalBuilderBot(self.get_game()),
            LocalSendBot(self.get_game()),
            LocalCollectionBot(self.get_game()),
            LocalDecorationBot(self.get_game()),
            LocalStorageBot(self.get_game()),
            LocalRouletteBot(self.get_game()),
            LocalBlackJackBot(self.get_game()),
            LocalBuffBot(self.get_game()),
            LocalMagicBot(self.get_game()),
            LocalResourceBot(self.get_game()),
            LocalCookBot(self.get_game()),
            LocalDiggerBot(self.get_game()),
            LocalCraftBot(self.get_game()),
            LocalPlantBot(self.get_game()),
            LocalPickupBot(self.get_game()),
            LocalBuyBot(self.get_game()),
            LocalTraderBot(self.get_game()),
            LocalLocationBot(self.get_game())
        ]

        event_handler = LocalEventHandler(self.get_game())

        return single_bots, circle_bots, event_handler
