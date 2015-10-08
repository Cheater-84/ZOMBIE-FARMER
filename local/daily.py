# -*- coding: utf-8 -*-

import logging
import random
from engine.game_types import DailyBonus, SendFreeGifts, SendGift, SendGiftItem
from engine.base import BaseBot
from engine.helpers import get_item_count
from engine.game_event import dict2obj

logger = logging.getLogger(__name__)


class LocalDailyBot(BaseBot):

    def __init__(self, game):
        super(LocalDailyBot, self).__init__(game)

        self.free_gifts = self.get_params().free_gifts
        self.low_level_gifts = self.get_params().low_level_gifts
        self.free_msg = self.get_params().free_msg
        self.low_level_msg = self.get_params().low_level_msg

    def perform_action(self):

        if not self.get_params().switch_local_daily_bot:
            return

        players = self.get_game_state().get_players()

        # Ежедневный бонус
        daily_bonus = self.get_game_state().get_state().dailyBonus
        if int(daily_bonus.playFrom) and self.get_timer().has_elapsed(daily_bonus.playFrom, 10):
            daily = DailyBonus()
            self.get_events_sender().send_game_events([daily])

            # Если можно крутнуть ежедневную рулетку,
            # Значит можно уже и дарить ежедневные подарочки
            self.get_game_state().get_state().freeGiftUsers = []

            # Сбрасываем палочки-выручалочки
            self.get_game_state().get_state().magic.used = 0
            self.get_game_state().get_state().magic.expire = unicode(86400000)

        free_gift_users = [x.user for x in self.get_game_state().get_state().freeGiftUsers]
        not_gift_users = [x for x in players
                          if x.id not in free_gift_users and x.id not in self.get_params().exclude_low_level]

        if not_gift_users:
            # Подарки нищебродам до 80 уровня
            # Максиммальное время отсутствия, не может быть больше 3 суток
            deadline = 3
            day_timestamp = 1000 * 60 * 60 * 24
            deadline_timestamp = deadline * day_timestamp

            pre_aways = [x for x in not_gift_users if hasattr(x, u'accessDate')]
            lst = [x for x in pre_aways if abs(int(x.accessDate)) < deadline_timestamp and x.level in xrange(40, 81)]

            for user in lst:
                if type(user) == unicode:
                    continue
                for low_level_gift in self.low_level_gifts:
                    if low_level_gift.name in user.liteGameState.wishlist:
                        # Если на складе нет нужного количества для подарка идем к следущему подарку
                        storage_count = self.get_game_state().count_storage(low_level_gift.name)
                        delta = get_item_count(low_level_gift, storage_count)

                        if delta:
                            # Выбрали подарок и дарим его
                            low_level_gift_obj = self.get_item_reader().get(low_level_gift.name)
                            gift_item = SendGiftItem(msg=self.low_level_msg, item=low_level_gift.name,
                                                     count=delta, user=user.id)
                            send_event = SendGift(gift=gift_item)
                            evts = self.get_events_sender().send_game_events([send_event])
                            evts += self.get_events_sender().send_game_events()

                            # Если успешно прошел подарок идем к следущему соседу по списку
                            filter_evts = [x.type for x in evts]
                            if u'alert' not in filter_evts:
                                friend = self.get_game_state().get_player(user.id)
                                user_name = friend.name if hasattr(friend, 'name') else user.id
                                logger.info(u'Отправляем для %s в подарок % s %i шт' %
                                            (user_name, low_level_gift_obj.name, delta))

                                if u'storage' in low_level_gift_obj.type:
                                    self.get_game_state().remove_storage(low_level_gift.name, delta)
                            break

            # Бесплатные подарки
            for free_gift in self.free_gifts:
                gift_obj = self.get_item_reader().get(free_gift)

                free_gift_users = [x.user for x in self.get_game_state().get_state().freeGiftUsers]
                lst = [x.id for x in players if free_gift in x.liteGameState.wishlist and x.id not in free_gift_users]

                if lst:
                    logger.info(u'Отправляем бесплатный подарок %s %i игрокам' % (gift_obj.name, len(lst)))
                    freegift_event = SendFreeGifts(msg=self.free_msg, itemId=gift_obj.id, userIds=lst)

                    self.get_events_sender().send_game_events([freegift_event])

                    while lst:
                        lst_item = lst.pop(0)
                        user_obj = dict2obj({'user': lst_item})
                        self.get_game_state().get_state().freeGiftUsers.append(user_obj)

            free_gift = random.choice(self.free_gifts)
            gift_obj = self.get_item_reader().get(free_gift)

            free_gift_users = [x.user for x in self.get_game_state().get_state().freeGiftUsers]
            lst = [x.id for x in players if x.id not in free_gift_users]

            if lst:
                logger.info(u'Отправляем бесплатный подарок %s %i игрокам' % (gift_obj.name, len(lst)))
                freegift_event = SendFreeGifts(msg=self.free_msg, itemId=gift_obj.id, userIds=lst)

                self.get_events_sender().send_game_events([freegift_event])

                while lst:
                    lst_item = lst.pop(0)
                    user_obj = dict2obj({'user': lst_item})
                    self.get_game_state().get_state().freeGiftUsers.append(user_obj)
