# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)


class BaseBot(object):

    def __init__(self, game):
        self.__game_state = game

    def get_game(self):
        return self.__game_state

    def get_item_reader(self):
        return self.get_game().game_item_reader

    def get_game_state(self):
        return self.get_game().game_state

    def get_events_sender(self):
        return self.get_game().game_events_sender

    def get_timer(self):
        return self.get_game().timer

    def get_api(self):
        return self.get_game().api

    def get_id(self):
        return unicode(self.get_game().game_initializer.get_api_user_id())

    def get_params(self):
        return self.get_game().params

    def get_statistic(self):
        return self.get_game().statistic


class Core(object):

    def __init__(self, game):
        self.__game = game

    def get_game(self):
        return self.__game

    def get_presets(self):
        return None

    def get_stop_condition(self):
        return False

    def run(self):
        single_bots, circle_bots, event_handler = self.get_presets()

        for single_bot in single_bots:
            single_bot.perform_action()
            event_handler.event_handle()

            if self.get_stop_condition():
                break

        while not self.get_stop_condition():
            for circle_bot in circle_bots:
                circle_bot.perform_action()
                event_handler.event_handle()

                if self.get_stop_condition():
                    break
