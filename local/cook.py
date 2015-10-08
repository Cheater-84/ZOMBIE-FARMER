# -*- coding: utf-8 -*-
import logging
from engine.game_types import GameCookGrave, GameCookGraveWithBrains, GameCookRecipe, StartWorker, StopWorker, \
    GamePickItem, CookSpeedup
from engine.base import BaseBot
from engine.helpers import get_item_count

logger = logging.getLogger(__name__)


class LocalCookBot(BaseBot):

    @staticmethod
    def get_worker_types():
        return [GameCookGrave.type, GameCookGraveWithBrains.type]

    def perform_action(self):

        if not self.get_params().switch_local_cook_bot:
            return

        cook_events = []
        pick_events = []
        speedup_events = []
        recipes = self.get_params().recipes

        if not recipes:
            return

        cook_graves = self.get_game_state().get_objects_by_types(self.get_worker_types())

        for cook_grave in cook_graves:
            cook_grave_obj = self.get_item_reader().get(cook_grave.item)
            # Если повар не работает, то отправляем его на работу
            if not cook_grave.isUp:
                start_evt = StartWorker(objId=cook_grave.id)
                evts = self.get_events_sender().send_game_events([start_evt])

                # Если от сервера пришло сообщение о том что нет мозгов,
                # то обрабатываем его сразу чтобы знать кто не будет работать
                no_brains = False
                for evt in evts:
                    if evt.type == u'alert':
                        if evt.msg == u'SERVER_NO_BRAINS':
                            no_brains = True
                if not no_brains:
                    logger.info(u'Отправляем работать %s %i' % (cook_grave_obj.name, cook_grave.id))
                    cook_grave.isUp = True
                    # Если у него есть рецепты в корзинках, то готовим их
                    if cook_grave.pendingRecipes:
                        cook_grave.currentRecipe = cook_grave.pendingRecipes.pop(0)

            # Солим рецепт если разрешено и есть соль на складе
            if self.get_params().allow_cook_speedup:
                if not cook_grave.speeduped:
                    speeduper_obj = self.get_item_reader().get(u'@RED_SPEEDUPER')
                    speeduper_count = self.get_game_state().count_storage(u'@RED_SPEEDUPER')
                    if speeduper_count:
                        logger.info(u'Используем %s для %s %i' %
                                    (speeduper_obj.name, cook_grave_obj.name, cook_grave.id))
                        speedup_evt = CookSpeedup(objId=cook_grave.id)
                        speedup_events.append(speedup_evt)
                        self.get_game_state().remove_storage(u'@RED_SPEEDUPER', 1)

            # Если у него есть бочки, их нужно собрать
            while cook_grave.materials:
                material_item = cook_grave.materials.pop(0)
                material = self.get_item_reader().get(material_item)
                logger.info(u'Забираем у %s %i %s 1 шт' % (cook_grave_obj.name, cook_grave.id, material.name))
                pick_item = GamePickItem(itemId=material.id, objId=cook_grave.id)
                pick_events.append(pick_item)

                # Добавляем на склад
                if u'storage' in material.type:
                    self.get_game_state().add_storage(material_item, 1)

                # Если есть рецепты еще, то ставим их на варение
                if cook_grave.pendingRecipes:
                    cook_grave.currentRecipe = cook_grave.pendingRecipes.pop(0)

            # Если сейчас ничего не варим
            if not hasattr(cook_grave, u'currentRecipe') and cook_grave.isUp or \
                (hasattr(cook_grave, u'currentRecipe') and
                 len(cook_grave.pendingRecipes) < self.get_params().cook_receipts - 1):

                current_count = 1 if hasattr(cook_grave, u'currentRecipe') else 0
                need_count = self.get_params().cook_receipts - len(cook_grave.pendingRecipes) - current_count
                while need_count:
                    for recipe in recipes:
                        # Берем рецепт
                        recipe_obj = self.get_item_reader().get(recipe.name)
                        storage_count = self.get_game_state().count_storage(recipe_obj.result)
                        delta = get_item_count(recipe, storage_count)
                        if delta:
                            # Проверяем наличие ингридиентов
                            ingridients = recipe_obj.ingridients
                            ingridients_enough = True
                            for ingridient in ingridients:
                                if self.get_game_state().count_storage(ingridient.item) < ingridient.count:
                                    ingridients_enough = False
                                    break

                            # Если нам хватает ингридиентов на рецепт, то варим его
                            if ingridients_enough:
                                logger.info(u'Начали готовить %s' % recipe_obj.name)
                                cook_event = GameCookRecipe(itemId=recipe_obj.id, objId=cook_grave.id)
                                cook_events.append(cook_event)
                                if not hasattr(cook_grave, u'currentRecipe'):
                                    cook_grave.currentRecipe = recipe.name
                                else:
                                    cook_grave.pendingRecipes.append(recipe.name)
                                break

                    need_count -= 1

            # Если повара без мозгов не начали работать,
            # то отправляем их спать, чтобы не занимать мозги
            if not hasattr(cook_grave, u'currentRecipe') and cook_grave_obj.id.find(u'BRAIN') == -1 and cook_grave.isUp:
                stop_evt = StopWorker(objId=cook_grave.id)
                self.get_events_sender().send_game_events([stop_evt])
                logger.info(u'Отправляем %s %i спать' % (cook_grave_obj.name, cook_grave.id))
                cook_grave.isUp = False

        # Шлем все на сервер
        self.get_events_sender().send_game_pack_events(speedup_events)
        self.get_events_sender().send_game_pack_events(pick_events)
        self.get_events_sender().send_game_pack_events(cook_events)
