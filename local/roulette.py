# -*- coding: utf-8 -*-

import logging
from engine.game_types import GameBuilding, GamePlayGame
from engine.base import BaseBot

logger = logging.getLogger(__name__)


class LocalRouletteBot(BaseBot):

    def __init__(self, game):
        super(LocalRouletteBot, self).__init__(game)

        self.casino_played = False

    def perform_action(self):

        if not self.get_params().switch_local_roulette_bot:
            return

        roll_events = []

        buildings = self.get_game_state().get_objects_by_types([GameBuilding.type])

        for building in list(buildings):
            building_item = self.get_item_reader().get(building.item)

            # Если постройка не готова, то идем к следущей
            if hasattr(building_item, 'upgrades'):
                if building.level < len(building_item.upgrades):
                    continue

            for game in building_item.games:
                game_id = game.id
                play_cost = None
                play_cost_info = u''
                if hasattr(game, 'playCost'):
                    play_cost = game.playCost
                    play_cost_obj = self.get_item_reader().get(play_cost.item)
                    play_cost_info = u' за %s %i шт' % (play_cost_obj.name, play_cost.count)
                next_play = None
                next_play_times = building.nextPlayTimes.__dict__
                if game_id in next_play_times:
                    next_play = int(next_play_times[game_id])

                if hasattr(game, 'playsCount'):
                    if game.playsCount == getattr(building.playsCounts, game.id, 0):
                        continue

                if building_item.id == 'B_SLOT_APPLE':
                    # Крутить рулетку в яблочном автомате за 5 яблок
                    if game_id == 'B_SLOT_B_ROULETTE1' and self.get_params().apple_roulette_1:
                        apple_count = self.get_game_state().count_storage(u'@S_51')
                        if apple_count >= 5 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@S_51', 5)
                            play_cost = None

                    # Крутить рулетку в яблочном автомате за 1 компот
                    elif game_id == 'B_SLOT_APPLE_ROULETTE2' and self.get_params().apple_roulette_2:
                        apple_count = self.get_game_state().count_storage(u'@R_56')
                        if apple_count >= 1 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@R_56', 1)
                            play_cost = None

                elif building_item.id == 'B_SLOT_CHERRY':
                    # Крутить рулетку в вишневом автомате за 5 вишни
                    if game_id == 'B_SLOT_B_ROULETTE1' and self.get_params().cherry_roulette_1:
                        cherry_count = self.get_game_state().count_storage(u'@S_52')
                        if cherry_count >= 5 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@S_52', 5)
                            play_cost = None

                    # Крутить рулетку в вишневом автомате за 1 джем
                    elif game_id == 'B_SLOT_CHERRY_ROULETTE2' and \
                            self.get_params().cherry_roulette_2:
                        cherry_count = self.get_game_state().count_storage(u'@R_57')
                        if cherry_count >= 1 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@R_57', 1)
                            play_cost = None

                elif building_item.id == 'B_SLOT_MANDARIN':
                    # Крутить рулетку в мандариновом автомате за 5 мандарин
                    if game_id == 'B_SLOT_B_ROULETTE1' and self.get_params().mandarin_roulette_1:
                        mandarin_count = self.get_game_state().count_storage(u'@S_53')
                        if mandarin_count >= 5 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@S_53', 5)
                            play_cost = None

                    # Крутить рулетку в мандариновом автомате за 1 мармелад
                    elif game_id == 'B_SLOT_MANDARIN_ROULETTE2' and self.get_params().mandarin_roulette_2:
                        mandarin_count = self.get_game_state().count_storage(u'@R_59')
                        if mandarin_count >= 1 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@R_59', 1)
                            play_cost = None

                elif building_item.id == 'B_SLOT_LEMON':
                    # Крутить рулетку в лимонном автомате за 5 лимонов
                    if game_id == 'B_SLOT_B_ROULETTE1' and self.get_params().lemon_roulette_1:
                        lemon_count = self.get_game_state().count_storage(u'@S_54')
                        if lemon_count >= 5 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@S_54', 5)
                            play_cost = None

                    # Крутить рулетку в лимонном автомате за 1 микс
                    elif game_id == 'B_SLOT_LEMON_ROULETTE2' and self.get_params().lemon_roulette_2:
                        lemon_count = self.get_game_state().count_storage(u'@R_58')
                        if lemon_count >= 1 and \
                                ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                            self.get_game_state().remove_storage(u'@R_58', 1)
                            play_cost = None

                # Крутить рулетку в аисте если есть больше 25 малины
                elif building_item.id == 'B_TREE_STORK' and game_id == 'B_TREE_STORK_ROULETTE':
                    if not self.get_params().stork_roulette:
                        continue

                    strawberry_count = self.get_game_state().count_storage(u'@S_57')
                    if strawberry_count >= 25 and \
                            ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                        self.get_game_state().remove_storage(u'@S_57', 25)
                        play_cost = None

                # Крутить рулетку в таверне если есть больше 5 дублонов и выполнен ряд требований:
                # 1. Мы не заключенный
                # 2. У нас нет еще пиратского сундука
                # 3. У нас один из статусов пирата
                elif building_item.id == 'B_TAVERNA' and game_id == 'B_TAVERNA_ROULETTE_1':
                    if not self.get_params().taverna_roulette_1:
                        continue
                    if (self.get_game_state().get_state().playerStatus != u'@PS_PRISONER' and
                       not self.get_game_state().count_storage_object(u'@PIRATE_BOX') and
                       not self.get_game_state().count_storage_object(u'@PIRATE_BOX_2') and
                       self.get_game_state().get_state().pirate.state in [u'CITIZEN', u'RETURNED', u'DEAD'] and
                       self.get_game_state().count_storage(u'@DUBLON') >= 5 and
                       ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None)):

                        self.get_game_state().remove_storage(u'@DUBLON', 5)
                        play_cost = None
                    else:
                        continue

                # Крутить рулетку в зомби-фортуне
                elif building_item.id == 'B_SLOT_B' and game_id == 'B_SLOT_B_ROULETTE1':
                    if not self.get_params().fortune_roulette_1:
                        continue
                    chip_count = self.get_game_state().count_storage(u'@O_CHIPS')
                    if not chip_count:
                        self.casino_played = False
                    if chip_count >= 5 and \
                            ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                        self.get_game_state().remove_storage(u'@O_CHIPS', 5)
                        play_cost = None
                    else:
                        continue

                # Крутить рулетку в казино
                elif building_item.id == 'B_CASINO':
                    if not self.get_params().casino_roulette:
                        continue
                    chip_count = self.get_game_state().count_storage(u'@O_CHIPS')
                    if self.get_timer().has_elapsed(next_play, 1) and not chip_count and not self.casino_played:
                        self.casino_played = True
                    else:
                        continue

                # Крутить рулетку в солдате если есть Глазной суп
                elif building_item.id == 'B_SOLDIER' and game_id == 'B_SOLDIER_ROULETTE':
                    if not self.get_params().soldier_roulette:
                        continue

                    soup_count = self.get_game_state().count_storage(u'@R_60')
                    if soup_count > 0 and \
                            ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                        self.get_game_state().remove_storage(u'@R_60', 1)
                        play_cost = None
                    else:
                        continue

                # Крутить рулетку в яйце
                elif 'B_EGG' in building_item.id:
                    if not self.get_params().egg_roulette:
                        continue
                    egg_count = self.get_game_state().count_storage(u'@EASTER_EGG')
                    if egg_count >= play_cost.count and \
                            ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None):
                        self.get_game_state().remove_storage(u'@EASTER_EGG', play_cost.count)
                        play_cost = None
                        plays_count = getattr(building.playsCounts, game.id, 0)
                        building.playsCounts.__setattr__(game_id, plays_count + 1)

                    else:
                        continue

                if ((next_play and self.get_timer().has_elapsed(next_play, 1)) or next_play is None) and \
                   play_cost is None and building.level == len(getattr(building_item, u'upgrades', [])):

                    logger.info(u'Крутим рулетку в %s %i%s (%i, %i)' %
                                (building_item.name, building.id, play_cost_info, building.x, building.y))

                    roll = GamePlayGame(building.id, game_id)
                    if building_item.id == 'B_CASINO' and self.get_params().casino_roulette:
                        evts = self.get_events_sender().send_game_events([roll])
                        for evt in evts:
                            if evt.type == u'game' and evt.extraId == u'SKLEP_FILL_CHIPS':
                                logger.info(u'Получили 10 фишек')
                                self.get_game_state().add_storage(u'@O_CHIPS', 10)
                                building.nextPlayTimes.__setattr__(evt.extraId, evt.nextPlayDate)
                    else:
                        roll_events.append(roll)

        self.get_events_sender().send_game_pack_events(roll_events)
