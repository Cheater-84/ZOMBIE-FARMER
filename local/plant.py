# -*- coding: utf-8 -*-
import logging
from engine.game_types import GamePlant, GameFruitTree, GameSlag, GameDigItem, GamePickItem, GameBuyItem, \
    FertilizeFruitTree, FertilizePlant
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalPlantBot(BaseBot):

    is_seed_complete = True

    events = []

    def perform_action(self):

        if not self.get_params().switch_local_plant_bot:
            return

        self.events = []

        self._pick_harvest()
        self._dig_harvest()
        self._seed_harvest()

        self.get_events_sender().send_game_pack_events(self.events)

    def _pick_harvest(self):

        harvest_items = self.get_game_state().get_objects_by_types([GamePlant.type, GameFruitTree.type])

        exp = 0
        for harvest_item in harvest_items:
            item = self.get_item_reader().get(harvest_item.item)
            if self.get_timer().has_elapsed(harvest_item.jobFinishTime, 1):
                pick_event = GamePickItem(objId=harvest_item.id)
                self.events.append(pick_event)
                self.get_game_state().add_storage(item.storageItem, 1)

                if harvest_item.type == GamePlant.type and harvest_item.item not in [u'@ZOLIAN1', u'@ZOLIAN2']:
                    harvest_item.type = 'Slag'
                    harvest_item.item = '@SLAG'
                    exp += item.xp
                elif harvest_item.type == GameFruitTree.type:
                    harvest_item.fruitingCount -= 1
                    logger.info(u'Собираем %s %i. Осталось %i шт' %
                                (item.name, harvest_item.id, harvest_item.fruitingCount))
                    if harvest_item.fruitingCount == 0:
                        self.get_game_state().remove_object_by_id(harvest_item.id)

                        if harvest_item.item in self.get_params().rebuy_fruit_tree_types:
                            box_pick = GamePickItem(objId=harvest_item.id)
                            harvest_rebuy = GameBuyItem(objId=harvest_item.id, itemId=item.id, x=harvest_item.x,
                                                        y=harvest_item.y)
                            self.events.append(box_pick)
                            self.events.append(harvest_rebuy)
                            logger.info(u'Сажаем заново %s %i (%i, %i)' %
                                        (item.name, harvest_item.id, harvest_item.x, harvest_item.y))
            else:
                # Если нашли дерево и разрешено удобрять
                if harvest_item.type == GameFruitTree.type and \
                   harvest_item.item in self.get_params().fertilized_tree_types:
                    fertilize_count = self.get_game_state().count_storage(u'@RED_TREE_FERTILIZER')
                    # Если хватает удобрений
                    if fertilize_count:
                        logger.info(u'Удобряем %s %i' % (item.name, harvest_item.id))
                        evt = FertilizeFruitTree(objId=harvest_item.id)
                        self.events.append(evt)
                        self.get_game_state().remove_storage(u'@RED_TREE_FERTILIZER', 1)

                if harvest_item.type == GamePlant.type and \
                        harvest_item.item in self.get_params().fertilized_plant_types:
                    fertilize_count = self.get_game_state().count_storage(u'@RED_FERTILIZER')
                    # Если хватает удобрений
                    if fertilize_count:
                        logger.info(u'Удобряем %s %i' % (item.name, harvest_item.id))
                        evt = FertilizePlant(objId=harvest_item.id)
                        self.events.append(evt)
                        self.get_game_state().remove_storage(u'@RED_FERTILIZER', 1)

        self.get_game_state().get_state().experience += exp

    def _dig_harvest(self):
        slags = self.get_game_state().get_objects_by_types([GameSlag.type])
        for slag in slags:
            dig_event = GameDigItem(slag.id)
            self.events.append(dig_event)
            slag.type = 'base'
            slag.item = '@GROUND'

            self.get_game_state().get_state().experience += 1

    def get_seed_item(self, seed_items):

        scales = []

        self.is_seed_complete = True
        for seed_arr_item in seed_items:
            seed_item = self.get_item_reader().get(seed_arr_item.name)
            # Если не можем еще его сажать, то идем к следущему
            if seed_item.level > self.get_game_state().get_state().level and \
                    seed_item.id not in self.get_game_state().get_state().shopOpened:
                continue
            seed_item_count = self.get_game_state().count_storage(seed_item.storageItem)

            # Если не указан максимум, значит сажаем растение без ограничений
            if not seed_arr_item.max:
                return seed_item

            # Если мы не набрали этот максимум на складе, то выбираем семена
            if not seed_item_count / seed_arr_item.max:
                return seed_item
            else:
                scales.append(seed_item_count / seed_arr_item.max)

        # Если не из чего выбирать, то выходим
        if not scales:
            return

        # Если набрали лимитам по всем растениям, то берем то что более нужно для посадки
        seed_item = self.get_item_reader().get(seed_items[scales.index(min(scales))].name)

        return seed_item

    def _seed_harvest(self):

        seed_items_dict = self.get_params().seed_items_dict
        current_loc_id = self.get_game_state().get_game_loc().id

        grounds = self.get_game_state().get_objects_by_items(['@GROUND', '@GROUND_1'])
        if grounds:

            seed_item_name = u''

            if seed_items_dict.get(current_loc_id):
                seed_items = seed_items_dict.get(current_loc_id)
            else:
                seed_items = seed_items_dict.get(u'other')

            seed_item = self.get_seed_item(seed_items)

            if not seed_item:
                return

            seed_item_count = 0
            for ground in grounds:
                seed_item_name = seed_item.name
                buy_event = GameBuyItem(unicode(seed_item.id), ground.id, ground.y, ground.x)
                self.events.append(buy_event)
                ground.type = u'plant'
                ground.item = unicode(seed_item.id)
                seed_item_count += 1

            if seed_item_count:
                logger.info(u'Посадили %s %i шт' % (seed_item_name, seed_item_count))
