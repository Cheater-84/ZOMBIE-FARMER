# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import GameBuyItem, GameSellGameObject, GameRemotePickItem, Magic, MoveToStorage, BuyResource
from engine.game_types import GameExchangeCollection

logger = logging.getLogger(__name__)


class LocalBuyBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_buy_bot:
            return

        for buy_item in self.get_params().buy_items:
            actions = {
                0: self.buy_and_magic,
                1: self.buy_and_sell,
                2: self.buy_and_pick,
                3: self.buy_and_storage,
                4: self.buy
            }
            actions.get(buy_item.mode)(buy_item)

    def buy_and_sell(self, buy_item):
        # Если тот остров
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in buy_item.location:

            decor_obj = self.get_item_reader().get(buy_item.item)

            # Если денег больше минимального ограничения
            if self.get_game_state().get_state().gameMoney >= decor_obj.buyCoins * buy_item.count:

                # Находим максимальный objId
                max_obj_id = 0L
                for go in self.get_game_state().get_state().gameObjects:
                    if go.id > max_obj_id:
                        max_obj_id = long(go.id)

                decor_count = 0
                logger.info(u'Начали покупать %s' % decor_obj.name)
                evts = []

                while decor_count < buy_item.count:
                    max_obj_id += 1
                    # Покупаем и ставим
                    buy_event = GameBuyItem(itemId=decor_obj.id, objId=max_obj_id, x=buy_item.x, y=buy_item.y)
                    evts.append(buy_event)

                    # Продаем
                    sell_evt = GameSellGameObject(objId=max_obj_id)
                    evts.append(sell_evt)

                    # Записываем опыт и списываем монетки
                    self.get_game_state().get_state().gameMoney -= decor_obj.buyCoins - decor_obj.sellCoins
                    self.get_game_state().get_state().experience += decor_obj.xp

                    decor_count += 1

                self.get_events_sender().send_game_pack_events(evts)

                if decor_count:
                    logger.info(u'Продали %s %i шт' % (decor_obj.name, decor_count))

    def buy_and_magic(self, buy_item):
        # Если нужный остров
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in buy_item.location:

            free_magic = 500 - self.get_game_state().get_state().magic.used
            # Если еще не использовали 500 палочек
            if free_magic:

                # Если нет палочек в наличии ставим сигнал на обмен хелла
                if self.get_game_state().count_storage(u'@MAGIC_WAND') >= free_magic:

                    buy_item_obj = self.get_item_reader().get(buy_item.item)

                    # Если хватит денег на трубы то идем дальше
                    if self.get_game_state().get_state().gameMoney > buy_item_obj.buyCoins * buy_item.count:

                        # Находим максимальный objId
                        max_obj_id = 0L
                        for go in self.get_game_state().get_state().gameObjects:
                            if go.id > max_obj_id:
                                max_obj_id = long(go.id)

                        decor_count = 0
                        evts = []
                        if decor_count < free_magic / buy_item_obj.materialCount:
                            logger.info(u'Начали покупать %s' % buy_item_obj.name)
                        
                        while decor_count < free_magic / buy_item_obj.materialCount:
                            max_obj_id += 1
                            # Покупаем и ставим
                            buy_event = GameBuyItem(itemId=buy_item_obj.id, objId=max_obj_id, x=buy_item.x,
                                                    y=buy_item.y)
                            evts.append(buy_event)

                            for _ in xrange(buy_item_obj.materialCount):
                                magic_event = Magic(objId=max_obj_id)
                                evts.append(magic_event)

                                self.get_game_state().get_state().magic.used += 1
                                self.get_game_state().add_storage(buy_item_obj.material, 1)
                                self.get_game_state().remove_storage(u'@MAGIC_WAND', 1)

                            self.get_game_state().get_state().experience += buy_item_obj.xp
                            self.get_game_state().get_state().gameMoney -= buy_item_obj.buyCoins
                            decor_count += 1

                        self.get_events_sender().send_game_pack_events(evts)
                        if decor_count:
                            logger.info(u'Установили и вырубили %s %i шт' %
                                        (buy_item_obj.name, free_magic / buy_item_obj.materialCount))

                # Если нужны палочки для вырубки, значит обмениваем ад, чтобы на складе
                else:
                    # Адская коллекция
                    hell_coll = u'C_34'

                    coll_obj = self.get_item_reader().get(hell_coll)
                    # Количество коллекций на складе
                    hell_count = self.get_game_state().count_collection(coll_obj.items)
                    # Необходимое количество коллекций, чтобы добить палочками лимит на сутки
                    hell_need = (free_magic - self.get_game_state().count_storage(u'@MAGIC_WAND')) / 15 + 1

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

    def buy_and_pick(self, buy_item):
        # Если тот остров
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in buy_item.location:

            valent_obj = self.get_item_reader().get(buy_item.item)

            # Если денег больше минимального ограничения
            if self.get_game_state().get_state().gameMoney > valent_obj.buyCoins * buy_item.count:

                # Находим максимальный objId
                max_obj_id = 0L
                for go in self.get_game_state().get_state().gameObjects:
                    if go.id > max_obj_id:
                        max_obj_id = long(go.id)

                decor_count = 0
                logger.info(u'Начали покупать %s' % valent_obj.name)
                evts = []

                while decor_count < buy_item.count:
                    max_obj_id += 1
                    # Покупаем и ставим
                    buy_event = GameBuyItem(itemId=valent_obj.id, objId=max_obj_id, x=buy_item.x, y=buy_item.y)
                    evts.append(buy_event)

                    # Продаем
                    sell_evt = GameRemotePickItem(objId=max_obj_id)
                    evts.append(sell_evt)

                    # Записываем опыт и списываем монетки
                    self.get_game_state().get_state().gameMoney -= valent_obj.buyCoins

                    decor_count += 1

                self.get_events_sender().send_game_pack_events(evts)

                if decor_count:
                    logger.info(u'Открыти %s %i шт' % (valent_obj.name, decor_count))

    def buy_and_storage(self, buy_item):
        # Если тот остров
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in buy_item.location:

            decor_obj = self.get_item_reader().get(buy_item.item)

            # Если денег больше минимального ограничения
            if self.get_game_state().get_state().gameMoney >= decor_obj.buyCoins * buy_item.count:

                # Находим максимальный objId
                max_obj_id = 0L
                for go in self.get_game_state().get_state().gameObjects:
                    if go.id > max_obj_id:
                        max_obj_id = long(go.id)

                decor_count = 0
                logger.info(u'Начали покупать %s' % decor_obj.name)
                evts = []

                while decor_count < buy_item.count:
                    max_obj_id += 1
                    # Покупаем и ставим
                    buy_event = GameBuyItem(itemId=decor_obj.id, objId=max_obj_id, x=buy_item.x, y=buy_item.y)
                    evts.append(buy_event)

                    # Продаем
                    sell_evt = MoveToStorage(objId=max_obj_id)
                    evts.append(sell_evt)

                    # Записываем опыт и списываем монетки
                    self.get_game_state().get_state().gameMoney -= decor_obj.buyCoins - decor_obj.sellCoins
                    self.get_game_state().get_state().experience += decor_obj.xp

                    decor_count += 1

                self.get_events_sender().send_game_pack_events(evts)

                if decor_count:
                    logger.info(u'Продали %s %i шт' % (decor_obj.name, decor_count))

    def buy(self, buy_item):
        # Если тот остров
        current_loc_id = self.get_game_state().get_game_loc().id
        if current_loc_id in buy_item.location:

            decor_obj = self.get_item_reader().get(buy_item.item)

            # Если денег больше минимального ограничения
            if (decor_obj.buyCoins and
                self.get_game_state().get_state().gameMoney >= decor_obj.buyCoins * buy_item.count) or \
                (decor_obj.buyCash and
                 self.get_game_state().get_state().gameMoney >= decor_obj.buyCash * buy_item.count):

                decor_count = 0
                logger.info(u'Начали покупать %s' % decor_obj.name)
                evts = []

                while decor_count < buy_item.count:
                    # Покупаем и ставим
                    buy_event = BuyResource(itemId=decor_obj.id, count=long(buy_item.count))
                    evts.append(buy_event)

                    decor_count += 1

                self.get_events_sender().send_game_pack_events(evts)

                if decor_count:
                    logger.info(u'Купили %s(%i) %i шт' % (decor_obj.name, decor_obj.count, decor_count))
            else:
                logger.info(u'Недостаточно средств для покупки %s(%i) %i шт' %
                            (decor_obj.name, decor_obj.count, buy_item.count))
