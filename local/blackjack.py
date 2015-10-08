# -*- coding: utf-8 -*-

import logging
from engine.game_types import BlackJack
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalBlackJackBot(BaseBot):

    suits = {
        u'H': u'Черви',
        u'S': u'Пики',
        u'D': u'Бубны',
        u'C': u'Трефы'
    }

    rangs = {
        2: u'Двойка',
        3: u'Тройка',
        4: u'Четверка',
        5: u'Пятерка',
        6: u'Шестерка',
        7: u'Семерка',
        8: u'Восьмерка',
        9: u'Девятка',
        10: u'Дестяка',
        11: u'Валет',
        12: u'Дама',
        13: u'Король',
        14: u'Туз'
    }

    dealer_cards = []
    player_cards = []

    bet = 5

    def perform_action(self):

        if not self.get_params().switch_local_blackjack_bot:
            return

        # Если нет фишек чтобы играть то выходим
        chip_count = self.get_game_state().count_storage(u'@O_CHIPS')
        if not chip_count:
            return

        buildings = self.get_game_state().get_objects_by_items([u'@B_CASINO'])
        if not buildings:
            return

        # Нашли казино
        building = buildings[0]
        building_obj = self.get_item_reader().get(building.item)

        # Если постройка не достроена то выходим
        if hasattr(building_obj, u'upgrades') and building.level < len(building_obj.upgrades):
            return

        # Если фишек хватает на очередную ставку
        while chip_count and chip_count >= self.bet:
            # Обнуляем карты
            self.dealer_cards = []
            self.player_cards = []

            logger.info(u'Начали игру за %i фишек. На счету %i фишек' % (self.bet, chip_count))

            # Играем
            results = self.play_game(building=building, bet=self.bet)

            # Подсчитываем очки и смотрим что за карты на руках
            player_sum, name_players_cards, dealer_sum = self.calc_cards()

            # Выводим результат
            for result in results:
                if result == u'BLACKJACK':
                    logger.info(u'БЛЭКДЖЕК')
                    cash = self.bet + self.bet / 2 if self.bet > 1 else self.bet + 1
                    self.get_game_state().add_storage(u'@O_CHIPS', cash)
                elif result == u'WIN':
                    logger.info(u'ВЫ ВЫИГРАЛИ набрав %i очков (%s) против %i очков у дилера' %
                                (player_sum, ', '.join(name_players_cards), dealer_sum))
                    self.get_game_state().add_storage(u'@O_CHIPS', self.bet)
                elif result == u'LOSE':
                    logger.info(u'ВЫ ПРОИГРАЛИ набрав %i очков (%s) против %i очков у дилера' %
                                (player_sum, ', '.join(name_players_cards), dealer_sum))
                    self.get_game_state().remove_storage(u'@O_CHIPS', self.bet)
                elif result == u'BUST':
                    logger.info(u'ПЕРЕБОР набрав %i очков (%s) против %i очков у дилера' %
                                (player_sum, ', '.join(name_players_cards), dealer_sum))
                    self.get_game_state().remove_storage(u'@O_CHIPS', self.bet)
                elif result == u'PUSH':
                    logger.info(u'НИЧЬЯ %i очков (%s) против %i очков у дилера' %
                                (player_sum, ', '.join(name_players_cards), dealer_sum))

            # Обновляем данные по фишкам
            chip_count = self.get_game_state().count_storage(u'@O_CHIPS')

    # Здесь стратегия, решает брать или не брать еще
    def resolve(self):
        rang_sum = 0

        # Наши очки
        for player_card in self.player_cards:
            if player_card.rang < 10:
                rang_sum += player_card.rang
            elif player_card.rang < 14:
                rang_sum += 10
            else:
                rang_sum += 11

        # Если мягкая стратегия, то смотрим на карту дилера и определяем до скольки набирать
        if self.dealer_cards[0].rang > 8:
            limit = 19
        else:
            limit = 18

        # Если набрали больше 21, то считаем что у нас есть туз,
        # а значит он считается за 1, это жесткая стратегия
        if rang_sum > 21:
            # Пересчитываем наши очки
            for player_card in self.player_cards:
                if player_card.rang < 10:
                    rang_sum += player_card.rang
                elif player_card.rang < 14:
                    rang_sum += 10
                else:
                    rang_sum += 1

            # Если жесткая стратегия то смотрим карту дилера и определяем до скольки набирать
            if self.dealer_cards[0].rang in [2, 3]:
                limit = 13
            elif self.dealer_cards[0].rang in [4, 5, 6]:
                limit = 12
            else:
                limit = 17

        # Если набрали до лимита прекращаем набор, если нет то добираем еще
        if rang_sum < limit:
            return True

        return False

    # Здесь просто собираем инфу для показа пользователю
    def calc_cards(self):
        player_sum = 0
        name_players_cards = []
        for player_card in self.player_cards:
            if player_card.rang < 10:
                player_sum += player_card.rang
            elif player_card.rang < 14:
                player_sum += 10
            else:
                player_sum += 11
            name_players_cards.append(u'%s %s' % (self.rangs.get(player_card.rang), self.suits.get(player_card.suit)))

        dealer_sum = 0
        for dealer_card in self.dealer_cards:
            if dealer_card.rang < 10:
                dealer_sum += dealer_card.rang
            elif dealer_card.rang < 14:
                dealer_sum += 10
            else:
                dealer_sum += 11

        return player_sum, name_players_cards, dealer_sum

    def play_game(self, building, bet):

        # Если незаконченная игра то обновляем данные
        if building.features[0].state == u'GAME':
            self.player_cards += building.features[0].slots
            self.dealer_cards += building.features[0].dealerCards
            bet = building.features[0].bet
            building.features[0].state = u'WAIT_DEAL'

        # Начинаем новую игру
        else:
            results = self.action(u'deal', building.id, bet)
            # Проверяем не закончилась ли игра
            if results:
                return results

        while True:
            # Если нужно взять еще, берем
            if self.resolve():
                results = self.action(u'hit', building.id, bet)
                # Проверяем не закончилась ли игра
                if results:
                    return results
            else:
                # Прекращаем набор и смотрим что у дилера
                results = self.action(u'stand', building.id, bet)
                return results

    def action(self, action, building_id, bet):
        action_evt = BlackJack(objId=building_id, action=action, bet=bet)
        evts = self.get_events_sender().send_game_events([action_evt])

        for evt in evts:
            if evt.type == u'blackjack':
                if evt.action == action:
                    self.dealer_cards += evt.dealerCards
                    self.player_cards += evt.playerCards

                    if hasattr(evt, 'results'):
                        return evt.results

                    return None
