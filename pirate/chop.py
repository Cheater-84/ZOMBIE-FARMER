# -*- coding: utf-8 -*-

import logging
from engine.game_types import PirateChopEvent
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class PirateChopBot(BaseBot):

    def perform_action(self):
        pirate_box = self.get_game_state().get_state().pirate
        chops = self.get_game_state().get_objects_by_types([u'chop'])
        chops.sort(key=lambda x: x.chopCount)

        chop_events = []

        for chop in chops:
            chop_obj = self.get_item_reader().get(chop.item)

            for instrument in pirate_box.instruments:
                instrument_obj = self.get_item_reader().get(instrument.item)
                if chop_obj.chopInstrumentType in instrument_obj.chopInstrumentType:
                    if chop_obj.chopCount < instrument.count:
                        logger.info(u'Рубим %s %i (%i ед.) с помощью %s (%i, %i)' %
                                    (chop_obj.name, chop.id, chop_obj.chopCount, instrument_obj.name, chop.x, chop.y))

                        instrument_evt = {
                            instrument_obj.id: chop_obj.chopCount
                        }
                        chop_event = PirateChopEvent(objId=chop.id, instruments=instrument_evt)
                        chop_events.append(chop_event)
                        instrument.count -= chop_obj.chopCount
                        self.get_game_state().remove_object_by_id(chop.id)
                        break

        self.get_events_sender().send_game_pack_events(chop_events)
