# -*- coding: utf-8 -*-

import logging
from engine.game_types import StartWorker, GameRemotePickItem, TradeExchange
from engine.game_event import dict2obj, obj2dict
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalTraderBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_trader_bot:
            return

        traders = self.get_game_state().get_objects_by_types([u'traderGrave'])

        for trader in traders:
            trader_obj = self.get_item_reader().get(trader.item)
            if not trader.started:
                start_evt = StartWorker(objId=trader.id)
                evts = self.get_events_sender().send_game_events([start_evt])

                # Если от сервера пришло сообщение о том что нет мозгов,
                # то обрабатываем его сразу чтобы знать кто не будет работать
                no_brains = False
                for evt in evts:
                    if evt.type == u'alert':
                        if evt.msg == u'SERVER_NO_BRAINS':
                            no_brains = True
                if not no_brains:
                    logger.info(u'Отправляем работать %s %i' % (trader_obj.name, trader.id))
                    trader.started = True

            # Если не меняется сейчас
            if not trader.countExchange:

                if not trader.countCompleted and self.get_params().mega_exchanges:
                    mega = self.get_params().mega_exchanges.pop(0)
                    exchange_evt = TradeExchange(objId=trader.id, user=None, give=mega.get('give'),
                                                 want=mega.get('want'))
                    self.get_events_sender().send_game_events([exchange_evt])
                    logger.info(u'Установили мега-обмен в %s %i' % (trader_obj.name, trader.id))

                old_trader_give = []
                old_trader_want = []

                # Если уже обменяли
                if trader.countCompleted:
                    give_str, want_str = u'', u''
                    old_trader_give = obj2dict(trader.give)
                    for give in trader.give:
                        give_item_obj = self.get_item_reader().get(give.item)
                        give_str = u', %s %i шт' if give_str else u'%s %i шт'
                        give_str = give_str % (give_item_obj.name, give.count)
                        if u'collectionItem' == give_item_obj.type:
                            self.get_game_state().remove_collection_item(give.item, give.count)
                        elif u'collection' == give_item_obj.type:
                            self.get_game_state().remove_collection(give_item_obj.items, give.count)
                        elif u'storage' in give_item_obj.type:
                            self.get_game_state().remove_storage(give.item, give.count)
                    old_trader_want = obj2dict(trader.want)
                    for want in trader.want:
                        want_item_obj = self.get_item_reader().get(want.item)
                        want_str = u', %s %i шт' if want_str else u'%s %i шт'
                        want_str = want_str % (want_item_obj.name, want.count)
                        if u'collectionItem' == want_item_obj.type:
                            self.get_game_state().add_collection_item(want.item, want.count)
                        elif u'collection' == want_item_obj.type:
                            self.get_game_state().add_collection(want_item_obj.items, want.count)
                        elif u'storage' in want_item_obj.type:
                            self.get_game_state().add_storage(want.item, want.count)
                    pick_evt = GameRemotePickItem(trader.id)
                    self.get_events_sender().send_game_events([pick_evt])
                    logger.info(u'%s  %i совершил обмен' % (trader_obj.name, trader.id))
                    logger.info(u'     Отдали %s' % give_str)
                    logger.info(u'     Приняли %s' % want_str)
                    trader.countCompleted = 0

                old_exchange = {
                    'gives': old_trader_give,
                    'wants': old_trader_want
                }

                # Кидаем новый обмен
                exchange = self.select_exchange(old_exchange)
                if not exchange:
                    continue

                trader.__setattr__(u'give', [])
                for my_give in exchange.get(u'gives', []):
                    trader.give.append(dict2obj(my_give))

                trader.__setattr__(u'want', [])
                for my_want in exchange.get(u'wants', []):
                    trader.want.append(dict2obj(my_want))

                exchange_evt = TradeExchange(objId=trader.id, user=None, give=exchange.get(u'gives', []),
                                             want=exchange.get(u'wants', []))
                self.get_events_sender().send_game_events([exchange_evt])

                logger.info(u'%s %i обновлен' % (trader_obj.name, trader.id))
                trader.countExchange = 1

    def select_exchange(self, exchange):

        gives = exchange.get(u'gives', [])
        if not gives:
            return None

        not_enough = False
        for give_item in gives:
            item, count = give_item.get(u'item'), give_item.get(u'count')
            give_obj = self.get_item_reader().get(item)
            if u'collectionItem' in give_obj.type:
                if self.get_game_state().count_collection_item(item) < count:
                    not_enough = True
            elif u'collection' in give_obj.type:
                if self.get_game_state().count_collection(give_obj.items) < count:
                    not_enough = True
            elif u'storage' in give_obj.type:
                if self.get_game_state().count_storage(item) < count:
                    not_enough = True

        if not not_enough:
            return exchange

        return None
