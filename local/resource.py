# -*- coding: utf-8 -*-
import logging
from engine.game_types import GamePickItem, GameGainItem, StopWorker, MoveToStorage
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalResourceBot(BaseBot):

    object_type_dict = {
        u'woodGrave': u'woodTree',
        u'woodGraveDouble': u'woodTree',
        u'stoneGrave': u'stone',
        u'stoneGraveDouble': u'stone'
    }

    curr_captured = []

    @staticmethod
    def get_worker_types():
        return [u'woodGrave', u'woodGraveDouble', u'stoneGrave', u'stoneGraveDouble']

    def select_target(self, grave):

        if grave.target:
            return True

        resources = self.get_game_state().get_objects_by_types(self.object_type_dict.get(grave.type))

        for resource in resources:
            if not resource.gainStarted and resource.id not in self.curr_captured:
                gain_event = GameGainItem(resource.id, grave.id)
                evts = self.get_events_sender().send_game_events([gain_event])

                # Если от сервера пришло сообщение о том что нет мозгов,
                # то обрабатываем его сразу чтобы знать кто не будет работать
                no_brains = False
                for evt in evts:
                    if evt.type == u'alert':
                        if evt.msg == u'SERVER_NO_BRAINS':
                            no_brains = True
                if not no_brains:
                    resource_obj = self.get_item_reader().get(resource.item)
                    logger.info(u'Выбираем для вырубки %s %i ед. (%i, %i)' %
                                (resource_obj.name, resource.materialCount, resource.x, resource.y))
                self.curr_captured.append(resource.id)
                return True
        return False

    def perform_action(self):

        if not self.get_params().switch_local_resource_bot:
            return

        grave_evts = []
        self.curr_captured = []

        graves = self.get_game_state().get_objects_by_types(self.get_worker_types())
        for grave in graves:
            if grave.materials:
                grave_obj = self.get_item_reader().get(grave.item)
                material_obj = self.get_item_reader().get(grave.materials[0])
                logger.info(u'Подбираем у %s %s %i шт' % (grave_obj.name, material_obj.name, len(grave.materials)))

                while grave.materials:
                    material_id = grave.materials.pop(0)
                    material_obj = self.get_item_reader().get(material_id)
                    pick_item = GamePickItem(itemId=material_obj.id, objId=grave.id)
                    grave_evts.append(pick_item)

            # self.select_target(grave)
            if not self.select_target(grave):
                stop_evt = StopWorker(objId=grave.id)
                storage_evt = MoveToStorage(objId=grave.id)
                grave_evts.append(stop_evt)
                grave_evts.append(storage_evt)

        self.get_events_sender().send_game_pack_events(grave_evts)
