# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import ChangeLocation

logger = logging.getLogger(__name__)


class LocalLocationBot(BaseBot):

    def __init__(self, game):
        super(LocalLocationBot, self).__init__(game)

        exclude_locations = self.get_params().exclude_locations

        location_info = self.get_game_state().get_state().locationInfos
        location_ids = [x.locationId for x in location_info]
        location_ids.insert(0, self.get_game_state().get_state().locationId)
        location_ids.sort(key=lambda var_x: (var_x.split(u'_')[0], self.get_item_reader().get(var_x).paid))

        self.locations = [x for x in location_ids if x not in exclude_locations and x not in [u'main']]
        self.locations.insert(0, u'main')

    def perform_action(self):

        if not self.get_params().switch_local_location_bot:
            return

        current_loc_id = self.get_game_state().get_game_loc().id
        next_loc_id = self.get_next_loc_id(current_loc_id)
        self.change_location(next_loc_id)

    def change_location(self, location_id):
        logger.info(u'Переходим на %s' % self.get_location_name(location_id))
        change_location_event = ChangeLocation(locationId=location_id)
        self.get_events_sender().send_game_events([change_location_event])

    def get_location_name(self, location_id):
        location_obj = self.get_item_reader().get(location_id)
        return location_obj.name

    def get_next_loc_id(self, location_id):
        locations = self.locations
        idx = locations.index(location_id) if location_id in locations else 0
        next_loc_id = locations[(idx + 1) % len(locations)]

        loc_obj = self.get_item_reader().get(next_loc_id)
        if loc_obj.paid:
            change_valid = False

            # ищем, есть ли у нас активированный бонус
            for l in self.get_game_state().get_state().buffs.list:
                if l.item in [u'@BUFF_TRAVEL_TICKET_TIME', u'@BUFF_TRAVEL_TICKET_TIME2']:
                    if not self.get_timer().has_elapsed(l.expire.endDate):
                        change_valid = True
                        break
                elif l.item in [u'@BUFF_TRAVEL_TICKET_COUNT', u'@BUFF_TRAVEL_TICKET_COUNT2']:
                    if l.expire.count:
                        change_valid = True
                        l.expire.count -= 1
                        break

            # Если переход на платный остров невозможен, то ищем дальше
            if not change_valid:
                next_loc_id = self.get_next_loc_id(next_loc_id)

        return next_loc_id
