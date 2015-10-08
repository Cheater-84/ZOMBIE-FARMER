# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import GameApplyGiftEvent, GameGift

logger = logging.getLogger(__name__)


class LocalGiftBot(BaseBot):

    def __init__(self, game):
        super(LocalGiftBot, self).__init__(game)

        self.apply_buy_gift = self.get_params().apply_buy_gift
        self.apply_premium_account_gift = self.get_params().apply_premium_account_gift
        self.admin_id = u'139890285'
        self.npc_id = u'ACTIVE_NPC_LOVE'

    def perform_action(self):

        if not self.get_params().switch_local_gift_bot:
            return

        gifts_events = []
        gifts = self.get_game_state().get_state().gifts

        for gift in gifts:
            gift_item = self.get_item_reader().get(gift.item)
            if gift_item.type == u'pickupBox' and gift_item.id in [u'VALENT_GIFT_BOX6']:
                continue

            with_message = hasattr(gift, 'msg') and gift.msg
            moved = gift_item.moved if hasattr(gift_item, 'moved') else False
            free = gift.free if hasattr(gift, 'free') else False
            denied_type = gift_item.type in [u'wood', u'stone']
            admin_gift = (gift.user in [self.admin_id, self.npc_id])
            msg = u'с сообщением: "%s" ' % gift.msg if with_message else u''

            if moved or admin_gift or denied_type:
                continue

            # Принимаем БП, Платные при включенном флаге, и Всё от своих игроков при включенном флаге
            if free or (not free and self.apply_buy_gift) or \
                    (gift.user in self.get_params().premium_accounts and self.apply_premium_account_gift):
                friend = self.get_game_state().get_player(gift.user)
                user_name = friend.name if hasattr(friend, 'name') else gift.user
                logger.info(u"Принимаем подарок %s %i шт %sот %s" % (gift_item.name, gift.count, msg, user_name))
                apply_gift_event = GameApplyGiftEvent(GameGift(gift.id))
                gifts_events.append(apply_gift_event)

                if u'storage' in gift_item.type:
                    self.get_game_state().add_storage(gift.item, gift.count)

                if u'collectionItem' in gift_item.type:
                    self.get_game_state().add_collection_item(gift_item.id, gift.count)

            gifts.remove(gift)

        self.get_events_sender().send_game_pack_events(gifts_events)
