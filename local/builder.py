# -*- coding: utf-8 -*-

import logging
from engine.game_types import BuildingUpgrade, CraftItem, Item
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalBuilderBot(BaseBot):
    
    # флаг, показывать ли недостающие для постройки материалы
    show_need_materials = True

    def perform_action(self):

        if not self.get_params().switch_local_builder_bot:
            return

        upgrade_evts = []
        need_materials, use_materials = {}, {}

        # список построек которые не нужно достраивать
        exclude_buildings = self.get_params().exclude_buildings

        # список построек
        buildings = self.get_game_state().get_objects_by_types(u'building')

        for building in buildings:
            building_obj = self.get_item_reader().get(building.item)

            # Если это недострой и он не в списке исключений
            if hasattr(building_obj, u'upgrades') and \
                    building.level < len(building_obj.upgrades) and \
                    (building.item not in exclude_buildings):

                # получаем ее текущий уровень постройки
                curr_upgrade = building_obj.upgrades[building.level]
                # награда за выполнение уровня
                bonus = curr_upgrade.xp

                # Смотрим, хватает ли материалов на постройку уровня
                enough = True
                for material in curr_upgrade.materials:
                    current_material_count = \
                        self.get_game_state().count_storage(material.item) - use_materials.get(material.item, 0)
                    # если материала хватает то записываем что мы его использовали
                    if current_material_count >= material.count:
                        use_count = use_materials.get(material.item, 0)
                        use_count += material.count
                        use_materials[material.item] = use_count
                    # если не хватает то записываем
                    else:
                        need_count = need_materials.get(material.item, 0)
                        need_count += material.count
                        need_materials[material.item] = need_count
                        enough = False

                # если всех материалов хватает то строим уровень
                if enough:
                    logger.info(u'Модернизируем %s %i до %i уровня' %
                                (building_obj.name, building.id, building.level + 1))
                    upgrade_evt = BuildingUpgrade(objId=building.id)
                    upgrade_evts.append(upgrade_evt)

                    # получаем бонус за постройку
                    self.get_game_state().get_state().experience += bonus

                    # списываем материалы
                    for material in curr_upgrade.materials:
                        material_obj = self.get_item_reader().get(material.item)
                        if u'storage' in material_obj.type:
                            self.get_game_state().remove_storage(material.item, material.count)

                        use_count = use_materials.get(material.item, 0)
                        use_count -= material.count
                        use_materials[material.item] = use_count

                    # постройка стала на уровень больше
                    building.level += 1

                    if building.level < len(building_obj.upgrades):
                        buildings.append(building)

        # отправляем все на сервер
        self.get_events_sender().send_game_pack_events(upgrade_evts)

        # Смотрим каких материалов не хватило
        for key in need_materials.keys():
            material_obj = self.get_item_reader().get(key)
            # сколько именно не хватило
            material_count = \
                need_materials.get(key, 0) + use_materials.get(key, 0) - self.get_game_state().count_storage(key)

            # получаем постройку где материал создается
            craft_objs = self.craft_buildings.get(key)
            if craft_objs:
                # заготовка для крафтинга этого материала
                craft_obj = craft_objs[0]

                # список что мы будем крафтить вообще
                will_crafts = self.get_params().crafts
                found = False

                # проходим по этому списку
                for will_craft in will_crafts:
                    # если в списке есть эта постройка
                    if will_craft.building == craft_obj.get(u'building'):
                        # и в ней уже задан нужный craft_id или же он пуст, т.е. создается всё возможное
                        if will_craft.craft_id is None or will_craft.craft_id == craft_obj.get(u'craft_id'):
                            # отмечаем что нашли такую позицию
                            found = True

                            # смотрим был ли там установлен сигнал для крафтинга.
                            # Если да, то активируем его, если нет то считаем что он и так будет создаваться
                            if will_craft.signal:
                                self.get_game_state().set_signal(will_craft.signal, True)

                            # смотрим был ли там установлен количество крафтинга.
                            # Если да, то ставим нужное количество, если нет то считаем что создасться максимум
                            if will_craft.count is not None:
                                will_craft.count = material_count
                            break

                # если не нашли такой постройки
                if not found:
                    # создаем сигнал для активации
                    self.get_game_state().set_signal(key, True)

                    # создаем новый параметр для крафтинга с нужным нам значением
                    will_crafts.append(CraftItem(
                        building=craft_obj.get(u'building'),
                        craft_id=craft_obj.get(u'craft_id'),
                        count=material_count,
                        signal=key
                    ))
            else:
                # получаем рецепт где материал создается
                receipt_name = self.craft_recipes.get(key)
                if receipt_name:
                    # список рецептов
                    recipes = self.get_params().recipes
                    found = False

                    # проходим по этому списку
                    for recipe in recipes:
                        # если в списке есть этот рецепт
                        if recipe.name == receipt_name:
                            # отмечаем что нашли такую позицию
                            found = True

                            # Если там указан максимум для склада, то проверяем,
                            # хватит ли нам или увеличиваем количество рецептов
                            if recipe.max:
                                if recipe.max - self.get_game_state().count_storage(key) < material_count:
                                    recipe.max = material_count + self.get_game_state().count_storage(key)
                            break

                    # если не нашли такой постройки
                    if not found:
                        # создаем новый рецепт поварам
                        recipes.append(Item(name=receipt_name, max=material_count))

            # Показываем требуемое количество материалов если установлен флаг
            if self.show_need_materials:
                logger.info(u'Для модернизации построек требуется %s %i шт' % (material_obj.name, material_count))

    # Для крафта, где что создать можно
    craft_buildings = {
        '@BLUE_FERTILIZER': [{u'building': u'@B_POOL', u'craft_id': 2}],
        '@BRAINS_1': [{u'building': u'@B_OSTANKINO', u'craft_id': 0}],
        '@BRAINS_8': [{u'building': u'@B_OSTANKINO', u'craft_id': 2}],
        '@BUFF_TRAVEL_TICKET_COUNT': [{u'building': u'@B_VAN_ICE_CREAM', u'craft_id': 2}],
        '@BUFF_TRAVEL_TICKET_COUNT2': [{u'building': u'@B_VAN_ICE_CREAM', u'craft_id': 3}],
        '@BUFF_TRAVEL_TICKET_TIME': [{u'building': u'@B_VAN_ICE_CREAM', u'craft_id': 0}],
        '@BUFF_TRAVEL_TICKET_TIME2': [{u'building': u'@B_VAN_ICE_CREAM', u'craft_id': 1}],
        '@COINS': [{u'building': u'@B_BUSINESS', u'craft_id': 2}],
        '@CR_01': [{u'building': u'@B_MILL', u'craft_id': 1}],
        '@CR_02': [{u'building': u'@B_CASTLE', u'craft_id': 1}],
        '@CR_03': [{u'building': u'@B_FLOWER', u'craft_id': 1}],
        '@CR_04': [{u'building': u'@B_UNIVERCITY', u'craft_id': 2}],
        '@CR_05': [{u'building': u'@B_UNIVERCITY', u'craft_id': 1}],
        '@CR_07': [{u'building': u'@B_PYRAMID', u'craft_id': 1}],
        '@CR_08': [{u'building': u'@B_SKLEP', u'craft_id': 1}],
        '@CR_09': [{u'building': u'@B_LIGHTHOUSE', u'craft_id': 0}],
        '@CR_10': [{u'building': u'@B_PYRAMID', u'craft_id': 0}],
        '@CR_11': [{u'building': u'@B_MILL', u'craft_id': 0}],
        '@CR_12': [{u'building': u'@B_NYTREE', u'craft_id': 1}],
        '@CR_13': [{u'building': u'@B_CASTLE', u'craft_id': 0}],
        '@CR_14': [{u'building': u'@B_SKLEP', u'craft_id': 1}],
        '@CR_15': [{u'building': u'@B_UNIVERCITY', u'craft_id': 3}],
        '@CR_17': [{u'building': u'@B_NYTREE', u'craft_id': 0}],
        '@CR_19': [{u'building': u'@B_LIGHTHOUSE', u'craft_id': 1}],
        '@CR_22': [{u'building': u'@B_LIGHTHOUSE', u'craft_id': 3}],
        '@CR_23': [{u'building': u'@B_PISA', u'craft_id': 0}],
        '@CR_27': [{u'building': u'@B_PYRAMID', u'craft_id': 3}],
        '@CR_28': [{u'building': u'@B_POOL', u'craft_id': 1}],
        '@CR_29': [{u'building': u'@B_LEADER', u'craft_id': 2}],
        '@CR_30': [{u'building': u'@B_OIL', u'craft_id': 0}],
        '@CR_32': [{u'building': u'@B_LEADER', u'craft_id': 0}],
        '@CR_33': [{u'building': u'@B_LEADER', u'craft_id': 1}],
        '@CR_34': [{u'building': u'@B_OIL', u'craft_id': 1}],
        '@CR_35': [{u'building': u'@B_UNIVERCITY', u'craft_id': 4}],
        '@CR_36': [{u'building': u'@B_JAPAN', u'craft_id': 1}],
        '@CR_37': [{u'building': u'@B_WHITEHOUSE', u'craft_id': 0}],
        '@CR_45': [{u'building': u'@B_STONEHANGE', u'craft_id': 1}],
        '@CR_48': [{u'building': u'@B_JAPAN', u'craft_id': 0}],
        '@CR_49': [{u'building': u'@B_CASTLE', u'craft_id': 2}],
        '@CR_50': [{u'building': u'@B_EIFFEL', u'craft_id': 1}],
        '@CR_53': [{u'building': u'@B_EIFFEL', u'craft_id': 0}],
        '@CR_54': [{u'building': u'@B_AES', u'craft_id': 0}],
        '@CR_56': [{u'building': u'@B_SPHINCS', u'craft_id': 0}],
        '@CR_58': [{u'building': u'@B_AES', u'craft_id': 1}],
        '@CR_59': [{u'building': u'@B_SKLEP', u'craft_id': 3}],
        '@CR_62': [{u'building': u'@B_WALL_F', u'craft_id': 1}],
        '@CR_63': [{u'building': u'@B_WALL_F', u'craft_id': 0}],
        '@CR_64': [{u'building': u'@B_TOWER', u'craft_id': 0}],
        '@CR_68': [{u'building': u'@B_BUSINESS', u'craft_id': 0}],
        '@CR_69': [{u'building': u'@B_UNIVERCITY', u'craft_id': 0}],
        '@CR_73': [{u'building': u'@B_WHEEL', u'craft_id': 4}],
        '@CR_75': [{u'building': u'@B_SCHOOL', u'craft_id': 0}],
        '@CR_77': [{u'building': u'@B_SCHOOL', u'craft_id': 1}],
        '@CR_85': [{u'building': u'@B_STONE_GARDEN', u'craft_id': 0}],
        '@CR_86': [{u'building': u'@B_JAPAN_LAKE', u'craft_id': 1}],
        '@CR_87': [{u'building': u'@B_JAPAN_LAKE', u'craft_id': 2}],
        '@CR_88': [{u'building': u'@B_STONE_GARDEN', u'craft_id': 1}],
        '@CR_89': [{u'building': u'@B_STONE_GARDEN', u'craft_id': 2}],
        '@CR_90': [{u'building': u'@B_STONE_GARDEN', u'craft_id': 3}],
        '@CR_91': [{u'building': u'@B_JAPAN_LAKE', u'craft_id': 0}],
        '@CR_98': [{u'building': u'@B_GUILDHALL', u'craft_id': 0}],
        '@CR_99': [{u'building': u'@B_GLOBE', u'craft_id': 0}],
        '@CR_101': [{u'building': u'@B_UNIVERSITY_EMERALD2', u'craft_id': 0}],
        '@CR_125': [{u'building': u'@B_BIG_CIRCUS', u'craft_id': 2}],
        '@CR_126': [{u'building': u'@B_CINEMA', u'craft_id': 0}],
        '@CR_127': [{u'building': u'@B_BIG_CIRCUS', u'craft_id': 1}],
        '@CR_130': [{u'building': u'@B_CINEMA', u'craft_id': 2}],
        '@CR_131': [{u'building': u'@B_BIG_CIRCUS', u'craft_id': 0}],
        '@CR_132': [{u'building': u'@B_CINEMA', u'craft_id': 1}],
        '@C_1_1': [{u'building': u'@B_WALL_C_EMERALD2', u'craft_id': 0}],
        '@C_1_2': [{u'building': u'@B_WALL_C_EMERALD2', u'craft_id': 1}],
        '@C_1_3': [{u'building': u'@B_WALL_C_EMERALD2', u'craft_id': 2}],
        '@C_1_4': [{u'building': u'@B_WALL_C_EMERALD2', u'craft_id': 3}],
        '@C_1_5': [{u'building': u'@B_WALL_C_EMERALD2', u'craft_id': 4}],
        '@C_14_1': [{u'building': u'@B_TOWER_EMERALD2', u'craft_id': 0}],
        '@C_14_2': [{u'building': u'@B_TOWER_EMERALD2', u'craft_id': 1}],
        '@C_14_3': [{u'building': u'@B_TOWER_EMERALD2', u'craft_id': 2}],
        '@C_14_4': [{u'building': u'@B_TOWER_EMERALD2', u'craft_id': 3}],
        '@C_14_5': [{u'building': u'@B_TOWER_EMERALD2', u'craft_id': 4}],
        '@C_2_1': [{u'building': u'@B_LIGHT_EMERALD2', u'craft_id': 0}],
        '@C_2_2': [{u'building': u'@B_LIGHT_EMERALD2', u'craft_id': 1}],
        '@C_2_3': [{u'building': u'@B_LIGHT_EMERALD2', u'craft_id': 2}],
        '@C_2_4': [{u'building': u'@B_LIGHT_EMERALD2', u'craft_id': 3}],
        '@C_2_5': [{u'building': u'@B_LIGHT_EMERALD2', u'craft_id': 4}],
        '@C_7_1': [{u'building': u'@B_MILL_EMERALD2', u'craft_id': 0}],
        '@C_7_2': [{u'building': u'@B_MILL_EMERALD2', u'craft_id': 1}],
        '@C_7_3': [{u'building': u'@B_MILL_EMERALD2', u'craft_id': 2}],
        '@C_7_4': [{u'building': u'@B_MILL_EMERALD2', u'craft_id': 3}],
        '@C_7_5': [{u'building': u'@B_MILL_EMERALD2', u'craft_id': 4}],
        '@C_22_1': [{u'building': u'@B_CASTLE_EMERALD2', u'craft_id': 0}],
        '@C_22_2': [{u'building': u'@B_CASTLE_EMERALD2', u'craft_id': 1}],
        '@C_22_3': [{u'building': u'@B_CASTLE_EMERALD2', u'craft_id': 2}],
        '@C_22_4': [{u'building': u'@B_CASTLE_EMERALD2', u'craft_id': 3}],
        '@C_22_5': [{u'building': u'@B_CASTLE_EMERALD2', u'craft_id': 4}],
        '@C_28_1': [{u'building': u'@B_OBSERVATORY', u'craft_id': 0}],
        '@C_28_2': [{u'building': u'@B_OBSERVATORY', u'craft_id': 1}],
        '@C_28_3': [{u'building': u'@B_OBSERVATORY', u'craft_id': 2}],
        '@C_28_4': [{u'building': u'@B_OBSERVATORY', u'craft_id': 3}],
        '@C_28_5': [{u'building': u'@B_OBSERVATORY', u'craft_id': 4}],
        '@C_36_1': [{u'building': u'@B_OBSERVATORY', u'craft_id': 5}],
        '@C_36_2': [{u'building': u'@B_OBSERVATORY', u'craft_id': 6}],
        '@C_36_3': [{u'building': u'@B_OBSERVATORY', u'craft_id': 7}],
        '@C_36_4': [{u'building': u'@B_OBSERVATORY', u'craft_id': 8}],
        '@C_36_5': [{u'building': u'@B_OBSERVATORY', u'craft_id': 9}],
        '@C_42_1': [{u'building': u'@B_OBSERVATORY', u'craft_id': 10}],
        '@C_42_2': [{u'building': u'@B_OBSERVATORY', u'craft_id': 11}],
        '@C_42_3': [{u'building': u'@B_OBSERVATORY', u'craft_id': 12}],
        '@C_42_4': [{u'building': u'@B_OBSERVATORY', u'craft_id': 13}],
        '@C_42_5': [{u'building': u'@B_OBSERVATORY', u'craft_id': 14}],
        '@GREEN_FERTILIZER': [{u'building': u'@B_TVSET', u'craft_id': 1}],
        '@RED_FERTILIZER': [{u'building': u'@B_TVSET', u'craft_id': 0}],
        '@R_02': [{u'building': u'@B_SHIP', u'craft_id': 0}],
        '@R_06': [{u'building': u'@B_SHIP', u'craft_id': 3}],
        '@R_09': [{u'building': u'@B_SHIP', u'craft_id': 1}],
        '@R_12': [{u'building': u'@B_SHIP', u'craft_id': 2}],
        '@R_27': [{u'building': u'@B_WHITEHOUSE', u'craft_id': 1}],
        '@SCASTLE_DIAMOND6': [{u'building': u'@SCASTLE_BLACKBOX', u'craft_id': 6}],
        '@SCASTLE_HOUSE1': [{u'building': u'@D_TIN_BOX_1', u'craft_id': 17}],
        '@SHOVEL_EXTRA': [{u'building': u'@B_EYE', u'craft_id': 1}],
        '@S_19': [{u'building': u'@B_PISA', u'craft_id': 2}],
        '@S_26': [{u'building': u'@B_PISA', u'craft_id': 1}],
        '@XP': [{u'building': u'@B_JAPAN', u'craft_id': 2}],
        '@ZOMBIE_YOUNG': [{u'building': u'@B_SKLEP', u'craft_id': 0}]
    }

    # Результаты рецептов
    craft_recipes = {
        '@CR_46': u'RECIPE_30',
        '@CR_47': u'RECIPE_31',
        '@CR_51': u'RECIPE_28',
        '@CR_52': u'RECIPE_29',
        '@CR_59': u'RECIPE_32',
        '@CR_79': u'RECIPE_36',
        '@CR_101': u'RECIPE_55',
        '@CR_119': u'RECIPE_56',
        '@R_01': u'RECIPE_01',
        '@R_02': u'RECIPE_02',
        '@R_03': u'RECIPE_03',
        '@R_04': u'RECIPE_04',
        '@R_05': u'RECIPE_05',
        '@R_06': u'RECIPE_06',
        '@R_07': u'RECIPE_07',
        '@R_08': u'RECIPE_08',
        '@R_09': u'RECIPE_09',
        '@R_10': u'RECIPE_10',
        '@R_11': u'RECIPE_11',
        '@R_12': u'RECIPE_12',
        '@R_13': u'RECIPE_13',
        '@R_14': u'RECIPE_14',
        '@R_15': u'RECIPE_15',
        '@R_16': u'RECIPE_16',
        '@R_17': u'RECIPE_17',
        '@R_18': u'RECIPE_18',
        '@R_19': u'RECIPE_19',
        '@R_20': u'RECIPE_20',
        '@R_21': u'RECIPE_21',
        '@R_22': u'RECIPE_22',
        '@R_23': u'RECIPE_23',
        '@R_24': u'RECIPE_24',
        '@R_25': u'RECIPE_25',
        '@R_26': u'RECIPE_26',
        '@R_27': u'RECIPE_27',
        '@R_29': u'RECIPE_33',
        '@R_30': u'RECIPE_34',
        '@R_31': u'RECIPE_37',
        '@R_32': u'RECIPE_38',
        '@R_33': u'RECIPE_39',
        '@R_34': u'RECIPE_41',
        '@R_35': u'RECIPE_46',
        '@R_36': u'RECIPE_43',
        '@R_37': u'RECIPE_48',
        '@R_38': u'RECIPE_44',
        '@R_39': u'RECIPE_40',
        '@R_52': u'RECIPE_42',
        '@R_53': u'RECIPE_45',
        '@R_54': u'RECIPE_47',
        '@R_55': u'RECIPE_49',
        '@R_56': u'RECIPE_50',
        '@R_57': u'RECIPE_51',
        '@R_58': u'RECIPE_52',
        '@R_59': u'RECIPE_53',
        '@R_60': u'RECIPE_54'
    }
