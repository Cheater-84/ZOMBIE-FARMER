# -*- coding: utf-8 -*-

import logging
from engine.game_types import RemoteTradeExchange
from remote.base import RemoteBot
from engine.helpers import prompt_query

logger = logging.getLogger(__name__)


class RemoteTraderBot(RemoteBot):

    def __init__(self, game):
        super(RemoteTraderBot, self).__init__(game)

        # Главная функция
        self.action = self.remote_trader

        # Что искать у торговцев
        self.trader_priorities = self.get_game().arg_params.get('trader_priorities')

        # Сторона обмена у торговцев
        self.trader_position = self.get_game().arg_params.get('trader_position')

    # Сторона обмена торговцев
    @staticmethod
    def get_trader_position():
        return {
            0: u'give',
            1: u'want'
        }

    # Торговцы
    @staticmethod
    def get_trader_items():
        return [u'@SC_TRADER_GRAVE', u'@SC_TRADER_GRAVE_COINS', u'@SC_TRADER_GRAVE_WITH_BRAINS']

    def remote_trader(self, event_to_handle):
        remote_game_objects = event_to_handle.gameObjects
        found_traders = []

        for go in remote_game_objects:
            # Если нашли работающего торговца
            if go.item in self.get_trader_items() and go.started and not go.countCompleted and go.countExchange:
                found = False
                # Проверяем. что стоит у него в продаже(покупке)
                for position in getattr(go, self.get_trader_position().get(self.trader_position)):
                    # проверяем наличие
                    for trader_priority in self.trader_priorities:
                        if position.item in self.get_params().trader_goods.get(trader_priority):
                            found = True
                            break
                    if found:
                        break

                if found:
                    found_traders.append(go.id)
                    go_name = self.get_item_reader().get(go.item).name
                    logger.info(u'   ***   %s %i(%i, %i)   ***   ' % (go_name, go.id, go.x, go.y))
                    for want in go.want:
                        want_name = self.get_item_reader().get(want.item).name
                        want_count = want.count
                        logger.info(u'Примет %s %i шт' % (want_name, want_count))
                    for give in go.give:
                        give_name = self.get_item_reader().get(give.item).name
                        give_count = give.count
                        logger.info(u'Отдаст %s %i шт' % (give_name, give_count))

        while found_traders:
            trader_variants = [u'Не обмениваем и идем дальше...']
            for found_trader in found_traders:
                trader_variants.append(u'Обмениваем торговца %i' % found_trader)
            allow_change = prompt_query(choice=trader_variants, show_line=False)
            if allow_change:
                checked_trader_id = found_traders.pop(allow_change - 1)
                if checked_trader_id:
                    for go in remote_game_objects:
                        if go.id == checked_trader_id:
                            check_storage_ok = True
                            # Проверяем. что стоит у него в продаже(покупке)
                            for position in go.want:
                                item_obj = self.get_item_reader().get(position.item)
                                count_item = 0
                                if u'collectionItem' == item_obj.type:
                                    count_item = self.get_game_state().count_collection_item(position.item)
                                elif u'collection' == item_obj.type:
                                    count_item = self.get_game_state().count_collection(item_obj.items)
                                elif u'storage' in item_obj.type:
                                    count_item = self.get_game_state().count_storage(position.item)

                                if count_item < position.count:
                                    check_storage_ok = False
                                    print u'Недостаточно %s. Требуется %i шт, в наличии %i шт' % \
                                          (item_obj.name, position.count, count_item)

                            if check_storage_ok:
                                print u'Обменяли торговца %i' % go.id
                                evt = RemoteTradeExchange(objId=go.id, give=go.want, want=go.give)
                                self.get_events_sender().send_game_events([evt])

                                # Списываем со склада
                                for position in go.want:
                                    item_obj = self.get_item_reader().get(position.item)
                                    if u'collectionItem' == item_obj.type:
                                        self.get_game_state().remove_collection_item(position.item, position.count)
                                    elif u'collection' == item_obj.type:
                                        self.get_game_state().remove_collection(item_obj.items, position.count)
                                    elif u'storage' in item_obj.type:
                                        self.get_game_state().remove_storage(position.item, position.count)
            else:
                return
