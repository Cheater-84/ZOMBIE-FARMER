# -*- coding: utf-8 -*-

import logging
from engine.game_types import PirateChopEvent
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class TropicChopBot(BaseBot):

    def perform_action(self):
        chops = self.get_game_state().get_objects_by_types([u'chop'])
        chops.sort(key=lambda x: x.chopCount, reverse=True)

        chop_events = []

        instruments = [u'@CHOP_MACHETE', u'@CHOP_AXE', u'@CHOP_HAMMER',
                       u'@CHOP_MACHETE_GOLDEN', u'@CHOP_AXE_GOLDEN', u'@CHOP_HAMMER_GOLDEN']

        for chop in chops:
            chop_obj = self.get_item_reader().get(chop.item)

            for instrument in instruments:
                instrument_obj = self.get_item_reader().get(instrument)
                if chop_obj.chopInstrumentType in instrument_obj.chopInstrumentType:
                    instrument_count = self.get_game_state().count_storage(instrument)
                    if chop_obj.chopCount < instrument_count:
                        logger.info(u'Рубим %s %i (%i ед.) с помощью %s (%i, %i)' %
                                    (chop_obj.name, chop.id, chop_obj.chopCount, instrument_obj.name,
                                     chop.x, chop.y))

                        instrument_evt = {
                            instrument_obj.id: chop_obj.chopCount
                        }
                        chop_event = PirateChopEvent(objId=chop.id, instruments=instrument_evt)
                        chop_events.append(chop_event)
                        self.get_game_state().remove_storage(instrument, chop_obj.chopCount)
                        self.get_game_state().remove_object_by_id(chop.id)
                        break

        self.get_events_sender().send_game_pack_events(chop_events)
