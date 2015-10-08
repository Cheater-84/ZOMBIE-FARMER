# -*- coding: utf-8 -*-

import logging
from engine.game_types import SendGift, SendGiftItem
from engine.base import BaseBot
from engine.helpers import get_item_count

logger = logging.getLogger(__name__)


class LocalSendBot(BaseBot):

    def __init__(self, game):
        super(LocalSendBot, self).__init__(game)

        self.send_accounts = self.get_params().send_accounts
        # friends = [unicode(x) for x in self.get_api().friends.getAppUsers()]
        # self.send_accounts = friends

        response = game.api.users.get(user_ids=u','.join(self.send_accounts))
        self.user_dict = {}
        for user_info in response:
            self.user_dict[unicode(user_info.get(u'uid'))] = u'%s %s' % \
                                                             (user_info.get(u'first_name'), user_info.get(u'last_name'))

    def perform_action(self):

        if not self.get_params().switch_local_send_bot:
            return

        if not self.send_accounts:
            return

        send_items = self.get_params().send_items

        for send_item in send_items:
            item_obj = self.get_item_reader().get(send_item.name)
            for send_account in self.send_accounts:
                if u'collection' in item_obj.type:
                    # Если указан только минимум и стоит флаг, пересылать все ддо минимума не равнями частями
                    if not self.get_params().send_equal_parts_collection and not send_item.count:
                        for coll_element in item_obj.items:
                            item_col_obj = self.get_item_reader().get(coll_element)
                            storage_count = self.get_game_state().count_collection_item(coll_element)
                            delta = get_item_count(send_item, storage_count)
                            if delta:
                                logger.info(u'Отправили %s %i шт на %s' %
                                            (item_col_obj.name, delta, self.user_dict.get(send_account)))
                                msg = self.get_params().send_account_msg
                                gift_item = SendGiftItem(msg=msg, item=coll_element, count=delta, user=send_account)
                                send_event = SendGift(gift=gift_item)
                                self.get_events_sender().send_game_events([send_event])

                                self.get_game_state().remove_collection_item(coll_element, delta)
                    else:
                        storage_count = self.get_game_state().count_collection(item_obj.items)
                        delta = get_item_count(send_item, storage_count)
                        if delta:
                            logger.info(u'Отправили %s %i шт на %s' %
                                        (item_obj.name, delta, self.user_dict.get(send_account)))
                            msg = self.get_params().send_account_msg
                            for coll_element in item_obj.items:
                                gift_item = SendGiftItem(msg=msg, item=coll_element, count=delta, user=send_account)
                                send_event = SendGift(gift=gift_item)
                                self.get_events_sender().send_game_events([send_event])

                                self.get_game_state().remove_collection_item(coll_element, delta)
                else:
                    storage_count = self.get_game_state().count_storage(send_item.name)
                    delta = get_item_count(send_item, storage_count)
                    if delta:
                        logger.info(u'Отправили %s %i шт на %s' %
                                    (item_obj.name, delta, self.user_dict.get(send_account)))
                        msg = self.get_params().send_account_msg
                        gift_item = SendGiftItem(msg=msg, item=send_item.name, count=delta, user=send_account)
                        send_event = SendGift(gift=gift_item)
                        self.get_events_sender().send_game_events([send_event])

                        self.get_game_state().remove_storage(send_item.name, delta)

            if not send_item.loop:
                send_items.remove(send_item)
