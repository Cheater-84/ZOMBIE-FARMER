# -*- coding: utf-8 -*-

import logging
from engine.game_types import SkipTask, GetMissions
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalMissionBot(BaseBot):

    def __init__(self, game):
        super(LocalMissionBot, self).__init__(game)

        self.allow_chapters = self.get_params().allow_chapters
        self.exclude_missions = []

    def perform_action(self):

        if not self.get_params().switch_local_mission_bot:
            return

        if not self.get_game_state().get_missions():
            logger.info(u'Получаем данные о квестах')
            self.get_events_sender().send_game_events([GetMissions()])
            return

        missions = self.get_valid_missions()

        for mission in missions:
            mission_obj = self.get_item_reader().get(mission.item)
            if not mission.disabled and not mission.finished:
                tasks = mission.tasks.__dict__
                for key in tasks:
                    task = tasks[key]
                    if not task.finished:
                        for x in mission_obj.tasks:
                            if x.id == key:
                                if hasattr(x, u'skipCash'):
                                    if self.get_game_state().get_state().cashMoney > x.skipCash:
                                        logger.info(u'Квест "%s". %s Пропускаем задание за %i ЗБ' %
                                                    (mission_obj.name, x.description, x.skipCash))
                                        evt = SkipTask(itemId=mission_obj.id, extraId=key)
                                        self.get_events_sender().send_game_events([evt])
                                    else:
                                        logger.info(u'Квест "%s". %s Недостаточно ЗБ для пропуска задания' %
                                                    (mission_obj.name, x.description))
                                        if mission_obj.id not in self.exclude_missions:
                                            self.exclude_missions.append(mission_obj.id)
                                else:
                                    if mission_obj.id not in self.exclude_missions:
                                        self.solve_task(mission_obj, x)

        if missions:
            self.get_events_sender().send_game_events([GetMissions()])
        else:
            self.get_params().switch_local_mission_bot = 0

    def get_valid_missions(self):
        missions = []
        for x in self.get_game_state().get_missions():
            x_obj = self.get_item_reader().get(x.item)
            if x_obj.id not in self.exclude_missions and not x.finished and not x.disabled:
                if x_obj.chapter in self.allow_chapters:
                    missions.append(x)
        return missions

    def solve_task(self, mission_obj, task):
        if task.type == u'buy':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'travelToLocation':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'upgradeBuilding':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'moveGameObjectToLocation':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            item_obj = self.get_item_reader().get(task.composition)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'place':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'craftItem':
            logger.info(u'Квест "%s". %s Задание нельзя пропустить за ЗБ' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
            if mission_obj.id not in self.exclude_missions:
                self.exclude_missions.append(mission_obj.id)
        elif task.type == u'setClothes':
            logger.info(u'Квест "%s". %s Выполняем задание' %
                        (mission_obj.name, task.description))
            for item in task.item:
                item_obj = self.get_item_reader().get(item)
                evt = {
                    u'type': u'settings',
                    u'playerSettings': {
                        u'hatId': item_obj.id,
                        u'dressId': None,
                        u'userName': u''
                    },
                    u"action": u"setPlayerSettings"
                }
                self.get_events_sender().send_game_events([evt])
                logger.info(u'')
