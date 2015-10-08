# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class RemoteBot(BaseBot):

    action = None

    def perform_action(self):
        remote_location = self.get_game_state().get_remote_loc()

        if not remote_location:
            return

        self.action(remote_location)