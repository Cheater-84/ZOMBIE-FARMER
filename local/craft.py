# -*- coding: utf-8 -*-
import logging
from engine.game_types import Craft, CraftItem
from engine.game_event import dict2obj
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalCraftBot(BaseBot):

    emerald_crafts = {
        '@C_42_1': {u'building': u'@B_OBSERVATORY', u'craft_id': 10},
        '@C_42_2': {u'building': u'@B_OBSERVATORY', u'craft_id': 11},
        '@C_42_3': {u'building': u'@B_OBSERVATORY', u'craft_id': 12},
        '@C_42_4': {u'building': u'@B_OBSERVATORY', u'craft_id': 13},
        '@C_42_5': {u'building': u'@B_OBSERVATORY', u'craft_id': 14}
    }

    def perform_action(self):

        if not self.get_params().switch_local_craft_bot:
            return

        # Если нужно крафтить изумрудку
        if self.get_params().allow_craft_emerald_collection:
            # Если нашли обсерваторию на острове
            buildings = self.get_game_state().get_objects_by_items([u'@B_OBSERVATORY'])

            if buildings:
                # Искомая постройка
                building = buildings[0]
                building_obj = self.get_item_reader().get(building.item)

                # Если постройка достроена то идем дальше
                if hasattr(building_obj, u'upgrades') and building.level == len(building_obj.upgrades):

                    # Проверяем количество бозонов и японки
                    bozon_count = self.get_game_state().count_storage(u'@CR_666')
                    japan_coll_obj = self.get_item_reader().get(u'C_36')
                    japan_count = self.get_game_state().count_collection(japan_coll_obj.items)

                    # Проверяем по таймерам возможность создавать всю коллекцию целиком
                    may_crafted_full_collection = True
                    next_play_times = building.nextPlayTimes.__dict__
                    for emerald, craft_obj in self.emerald_crafts.items():
                        craft = building_obj.crafts[craft_obj.get(u'craft_id')]
                        if not self.get_timer().has_elapsed(next_play_times[craft.craftId], 1):
                            may_crafted_full_collection = False

                    # ставим сигнал на крафтинг изумрудки, если есть что создать, и позволяет таймер
                    if min([bozon_count / 5, japan_count / 10]) and may_crafted_full_collection:

                        for emerald, craft_obj in self.emerald_crafts.items():
                            found = False

                            # проходим по этому списку
                            for will_craft in self.get_params().crafts:
                                # если в списке есть эта постройка
                                if will_craft.building == craft_obj.get(u'building'):
                                    # и в ней уже задан нужный craft_id или же он пуст, т.е. создается всё возможное
                                    if will_craft.craft_id is None or \
                                       will_craft.craft_id == craft_obj.get(u'craft_id'):
                                        # отмечаем что нашли такую позицию
                                        found = True

                                        # смотрим был ли там установлен сигнал для крафтинга.
                                        # Если да, то активируем его, если нет то считаем что он и так будет создаваться
                                        if will_craft.signal:
                                            self.get_game_state().set_signal(will_craft.signal, True)

                                        # смотрим был ли там установлен количество крафтинга.
                                        # Если да, то ставим нужное количество,
                                        # если нет то считаем что создасться максимум
                                        will_craft.count = bozon_count / 5
                                        break

                            # если не нашли такой постройки
                            if not found:
                                # создаем сигнал для активации
                                self.get_game_state().set_signal(emerald, True)

                                # создаем новый параметр для крафтинга с нужным нам значением
                                self.get_params().crafts.append(CraftItem(
                                    building=craft_obj.get(u'building'),
                                    craft_id=craft_obj.get(u'craft_id'),
                                    count=1,
                                    signal=emerald
                                ))

        # Список для крафтинга всего остального
        crafts = self.get_params().crafts
        for craft_obj in crafts:

            # Если нет сигнала о том, что нужно создавать
            if craft_obj.signal is not None and \
                    not self.get_game_state().get_signal(craft_obj.signal):
                continue

            buildings = self.get_game_state().get_objects_by_items([craft_obj.building])
            # Если нет постройки для создания то ищем дальше
            if not buildings:
                continue

            # Искомая постройка
            building = buildings[0]
            building_obj = self.get_item_reader().get(building.item)

            # Если постройка не достроена то идем дальше
            if hasattr(building_obj, u'upgrades') and building.level < len(building_obj.upgrades):
                continue

            # Если не указан craft_id значит создаем все что возможно в постройке
            if craft_obj.craft_id is not None:
                crafts_list = [building_obj.crafts[craft_obj.craft_id]]
            else:
                crafts_list = building_obj.crafts

            for craft in crafts_list:
                craft_events, res = [], []
                # Ищем количество которое возможно создать
                for material in craft.materials:
                    material_obj = self.get_item_reader().get(material.item)
                    if u'collection' in material_obj.type:
                        balance = 0 if craft_obj.count else 300
                        coll_item_count = \
                            (self.get_game_state().count_collection_item(material.item) - balance) / material.count
                        coll_item_count = coll_item_count if coll_item_count >= 0 else 0
                        res.append(coll_item_count)
                    elif u'storage' in material_obj.type:
                        if material_obj.id == u'COINS':
                            coins_item_count = self.get_game_state().get_state().gameMoney / material.count
                            res.append(coins_item_count)
                        else:
                            storage_item_count = self.get_game_state().count_storage(material.item) / material.count
                            res.append(storage_item_count)

                # Если мы указали количество создаваемых элементов, то смотрим
                # можем ли мы создать такое количество
                # В другом случае создаем максимально возможное значение
                if craft_obj.count:
                    craft_count = craft_obj.count if min(res) / craft_obj.count else 0
                else:
                    craft_count = min(res)

                # Создаем требуемое количество элементов
                if craft_count:
                    for i in xrange(craft_count):
                        craft_event = Craft(itemId=craft.id, objId=building.id)
                        craft_events.append(craft_event)

                    self.get_events_sender().send_game_pack_events(craft_events)

                    # Снимаем сигнал к созданию элементов
                    if craft_obj.signal is not None:
                        self.get_game_state().set_signal(craft_obj.signal, False)

                    # Смотрим на результат создания
                    total = craft.resultCount * craft_count
                    craft_result_obj = self.get_item_reader().get(craft.result)

                    logger.info(u'Создали в %s %s %i шт' % (building_obj.name, craft_result_obj.name, total))

                    # Списываем материал или коллекции
                    for material in craft.materials:
                        material_obj = self.get_item_reader().get(material.item)
                        if u'collection' in material_obj.type:
                            self.get_game_state().remove_collection_item(
                                material.item, material.count * craft_count)

                        elif u'storage' in material_obj.type:
                            if material_obj.id == u'COINS':
                                self.get_game_state().get_state().gameMoney -= material.count * craft_count
                            else:
                                self.get_game_state().remove_storage(material.item, material.count * craft_count)

                    # Добавляем результат в коллекции
                    if u'collection' in craft_result_obj.type:
                        self.get_game_state().add_collection_item(craft_result_obj.id, total)

                    # Добавляем результат на склад
                    if u'storage' in craft_result_obj.type:
                        if craft_result_obj.id == u'COINS':
                            self.get_game_state().get_state().gameMoney += total
                        else:
                            self.get_game_state().add_storage(craft.result, total)

                    # Добавляем результат в буфф если это проездной
                    if u'travelTicketBuff' in craft_result_obj.type:
                        buff_duration = self.get_item_reader().get(craft_result_obj.id).expire.duration
                        buff_type = self.get_item_reader().get(craft_result_obj.id).expire.type

                        expire = dict2obj({
                            u'endDate': unicode(buff_duration * 1000),
                            u'type': buff_type
                        })
                        new_buff = dict2obj({
                            u'item': '@%s' % craft_result_obj.id,
                            u'expire': expire
                        })

                        self.get_game_state().get_state().buffs.list.append(new_buff)
