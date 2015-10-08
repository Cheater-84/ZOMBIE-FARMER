# -*- coding: utf-8 -*-

import logging
from engine.game_types import Magic, GameExchangeCollection
from engine.base import BaseBot
from engine.game_event import dict2obj

logger = logging.getLogger(__name__)


class LocalMagicBot(BaseBot):

    magic_limit = 500

    def perform_action(self):

        if not self.get_params().switch_local_magic_bot:
            return

        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id not in self.get_params().allow_magic_locations:
            return

        # Если уже использовали 500 палочек
        if self.get_game_state().get_state().magic.used == self.magic_limit:
            return

        # Если нет палочек в наличии
        if not self.get_game_state().count_storage(u'@MAGIC_WAND'):
            self.get_game_state().set_signal(u'hell_coll', True)
            return

        events = []
        gain_list = self.get_game_state().get_objects_by_types(['woodTree', 'stone'])

        for gain_item in gain_list:
            if not gain_item.gainStarted:
                magic_obj = self.get_item_reader().get(gain_item.item)
                logger.info(u'Вырубаем палочками %s(%i) %i (%i, %i)' %
                            (magic_obj.name, gain_item.materialCount, gain_item.id, gain_item.x, gain_item.y))

                while gain_item.materialCount:
                    magic_event = Magic(objId=gain_item.id)
                    events.append(magic_event)
                    gain_item.materialCount -= 1
                    self.get_game_state().get_state().magic.used += 1
                    self.get_game_state().add_storage(magic_obj.material, 1)
                    self.get_game_state().remove_storage(u'@MAGIC_WAND', 1)

                    # Если уже использовали 500 палочек, то прекращаем вырубку ресурса
                    if self.get_game_state().get_state().magic.used == self.magic_limit:
                        break

                    # Если нет палочек в наличии, то прекращаем вырубку ресурса
                    if not self.get_game_state().count_storage(u'@MAGIC_WAND'):
                        self.get_game_state().set_signal(u'hell_coll', True)
                        break

                # Если вырубили до конца, то ставим ящик вместо дерева
                if not gain_item.materialCount:
                    if hasattr(magic_obj, 'box'):
                        box_item = self.get_item_reader().get(magic_obj.box)
                        new_obj = dict2obj({
                            'item': magic_obj.box,
                            'type': 'pickup',
                            'id': gain_item.id,
                            'x': gain_item.x,
                            'y': gain_item.y
                        })
                        self.get_game_state().remove_object_by_id(gain_item.id)
                        self.get_game_state().append_object(new_obj)
                        logger.info(u'%s превращён в %s' % (magic_obj.name, box_item.name))
                    else:
                        self.get_game_state().remove_object_by_id(gain_item.id)

            # Если уже использовали 500 палочек, то прекращаем поиск ресурсов
            if self.get_game_state().get_state().magic.used == self.magic_limit:
                break

            # Если нет палочек в наличии, то прекращаем вырубку ресурса
            if not self.get_game_state().count_storage(u'@MAGIC_WAND'):
                self.get_game_state().set_signal(u'hell_coll', True)
                break

        self.get_events_sender().send_game_pack_events(events)

        # Если получен сигнал, что нужны палочки для вырубки, значит обмениваем ад, чтобы на складе
        if self.get_game_state().get_signal(u'hell_coll'):
            # Адская коллекция
            hell_coll = u'C_34'

            coll_obj = self.get_item_reader().get(hell_coll)
            # Количество коллекций на складе
            hell_count = self.get_game_state().count_collection(coll_obj.items)
            # Необходимое количество коллекций, чтобы добить палочками лимит на сутки
            hell_need = (self.magic_limit - self.get_game_state().get_state().magic.used -
                         self.get_game_state().count_storage(u'@MAGIC_WAND')) / 15 + 1

            # Берем минимум сколько можем обменять: либо сколько надо, либо сколько есть
            delta = long(min([hell_count, hell_need]))

            changed_colls = self.get_params().changed_colls
            # Если у нас задан минимум для это коллекции, то берем с учетом минимума
            for changed_coll in changed_colls:
                if changed_coll.name == hell_coll and changed_coll.min < hell_count:
                    delta = long(min([hell_count - changed_coll.min, hell_need]))

            # Если есть, что менять
            if delta:
                logger.info(u'Обменяли %s %i шт' % (coll_obj.name, delta))
                exchange_coll_event = GameExchangeCollection(itemId=hell_coll, count=delta)
                self.get_events_sender().send_game_events([exchange_coll_event])

                # Списываем коллекции
                self.get_game_state().remove_collection(coll_obj.items, delta)

                # Добавляем палочки на склад
                for prize in coll_obj.prizes:
                    self.get_game_state().add_storage(prize.item, prize.count * delta)

                # Снимаем сигнал на создание палочек
                self.get_game_state().set_signal(u'hell_coll', False)
