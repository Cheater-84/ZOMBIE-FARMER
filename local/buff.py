# -*- coding: utf-8 -*-
import logging
from engine.game_types import GameUseStorageItem
from engine.base import BaseBot
from engine.game_event import dict2obj

logger = logging.getLogger(__name__)


class LocalBuffBot(BaseBot):

    def __init__(self, game):
        super(LocalBuffBot, self).__init__(game)

        # словарь с бонусами
        self.buff_dict = {
            'digger_buff': [u'@BS_BUFF_FIX_DIGGER1', u'@BS_BUFF_FIX_DIGGER2', u'@BS_BUFF_FIX_DIGGER3'],
            'cook_buff': [u'@BUFF_FIX_COOK_1', u'@BUFF_FIX_COOK_2', u'@BUFF_FIX_COOK_3'],
            'gain_buff': [u'@BUFF_FIX_GAIN1', u'@BUFF_FIX_GAIN2', u'@BUFF_FIX_GAIN3'],
            'harvest_buff': [u'@BS_BUFF_FIX_HARVEST_1', u'@BS_BUFF_FIX_HARVEST_2', u'@BS_BUFF_FIX_HARVEST_3'],
            'travel_buff': [u'@BUFF_TRAVEL_TICKET_TIME', u'@BUFF_TRAVEL_TICKET_TIME2']
        }

    def perform_action(self):

        if not self.get_params().switch_local_buff_bot:
            return

        # проходим по ним
        for signal_name in self.buff_dict:
            # если мы должны его активировать при необходимости
            if getattr(self.get_params(), signal_name):

                # считаем что бонус нужно активировать
                need_buff = True
                # получаем список возможных бонусов по данному типу
                buffs = self.buff_dict.get(signal_name)

                # ищем, есть ли у нас активированный бонус
                for l in self.get_game_state().get_state().buffs.list:
                    # если он еще активен, то помечаем что данный бонус пока не нужно активировать
                    for buff in buffs:
                        buff_obj = self.get_item_reader().get(buff)

                        if hasattr(buff_obj, 'items'):
                            if buff_obj.items[0].item == l.item:
                                need_buff = self.get_timer().has_elapsed(l.expire.endDate, -10)
                        else:
                            l_obj = self.get_item_reader().get(l.item)
                            if buff_obj.id == l_obj.id:
                                need_buff = self.get_timer().has_elapsed(l.expire.endDate, -10)

                # если все-таки нужно активировать
                if need_buff:
                    # если это проездной то ставим сигнал для крафтинга
                    if signal_name == u'travel_buff':
                        self.get_game_state().set_signal(u'travel_buff', True)
                        return

                    # для всех остальных активируем со склада
                    for buff in buffs:
                        # смотрим сколько у нас на складе есть
                        buff_count = self.get_game_state().count_storage(buff)

                        # если есть то активируем
                        if buff_count:
                            buff_obj = self.get_item_reader().get(buff)
                            buff_duration = self.get_item_reader().get(buff_obj.items[0].item).expire.duration
                            buff_type = self.get_item_reader().get(buff_obj.items[0].item).expire.type

                            buff_event = GameUseStorageItem(itemId=buff_obj.id)
                            self.get_events_sender().send_game_events([buff_event])

                            logger.info(u'Активируем %s' % buff_obj.name)

                            # создаем новый объект-бонус для записи в гейм-стейт
                            expire = dict2obj({
                                u'endDate': unicode(buff_duration * 1000),
                                u'type': buff_type
                            })

                            new_buff = dict2obj({
                                u'item': buff_obj.items[0].item,
                                u'expire': expire
                            })

                            # записываем в геймстейт новый бонус
                            self.get_game_state().get_state().buffs.list.append(new_buff)
                            break
