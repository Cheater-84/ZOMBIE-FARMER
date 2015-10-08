# -*- coding: utf-8 -*-

import logging
from remote.base import BaseBot
from engine.game_event import dict2obj

logger = logging.getLogger(__name__)


class RemoteEventHandler(BaseBot):

    def __init__(self, game):
        super(RemoteEventHandler, self).__init__(game)

        self.remote_scenary = self.get_game().arg_params.get('scenary')

        self.event_actions = {
            'playersInfo': self.players_info_event,
            'gameState': self.game_state_event,
            'pickup': self.pickup_event,
            'item': self.item_event
        }

    def event_handle(self):

        if not self.get_events_sender().get_game_events():
            self.get_events_sender().send_game_events()

        for event in self.get_events_sender().get_game_events():
            action = self.event_actions.get(event.type)
            if action:
                action(event)

        self.get_events_sender().clear_game_events()

    def game_state_event(self, event):
        self.get_game_state().set_remote_loc(event)
        self.get_game_state().exclude_user_id()

    def pickup_event(self, event):
        if event.action == u'add' and event.pickups:
            self.get_game_state().add_pickups(event.pickups)

    def item_event(self, event):
        if event.action == u'sendNewYearGift':
            new_year_object = dict2obj({u'treeId': event.objId, u'user': event.id})
            self.get_game_state().get_state().remoteNewYear.append(new_year_object)

    def players_info_event(self, event):

        players = event.players
        players = [x for x in players if x.playerStatus not in [u'@PS_PRISONER']]

        if self.remote_scenary in [2, 4]:
            players = [x for x in players if x.liteGameState.haveTreasure]

        saved_players = self.get_game_state().get_players()
        saved_players += players
        saved_players.sort(key=lambda var_x: var_x.level, reverse=True)

        if self.remote_scenary in [0, 1]:
            premium_accounts = self.get_params().premium_accounts
            premium_accounts.reverse()
            for premium_account in premium_accounts:
                saved_players_ids = [x.id for x in saved_players if x.id not in self.get_params().exclude_fir]
                if premium_account in saved_players_ids:
                    index = saved_players_ids.index(premium_account)
                    saved_player = saved_players.pop(index)
                    saved_players.insert(0, saved_player)

        self.get_game_state().set_players(saved_players)
