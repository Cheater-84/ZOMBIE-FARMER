# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_event import dict2obj

logger = logging.getLogger(__name__)


class LocalEventHandler(BaseBot):

    def __init__(self, game):
        super(LocalEventHandler, self).__init__(game)

        self.event_actions = {
            'playersInfo': self.players_info_event,
            'gift': self.gift_event,
            'gameState': self.game_state_event,
            'pickup': self.pickup_event,
            'cook': self.cook_event,
            'timeGain': self.time_gain_event,
            'plant': self.plant_event,
            'game': self.game_event,
            'gainMaterial': self.gain_material_event,
            'dailyBonus': self.daily_bonus_event,
            'action': self.action_event,
            'buried': self.buried_event,
            'buyedBrains': self.buyed_brains_event,
            'bridge': self.bridge_event,
            'unblock': self.unblock_event,
            'gameObject': self.game_object_event,
            'mission': self.mission_event
        }

    def event_handle(self):

        for event in self.get_events_sender().get_game_events():
            action = self.event_actions.get(event.type)
            if action:
                action(event)
            else:
                pass

        self.get_events_sender().clear_game_events()

    def gift_event(self, event):
        if event.action == 'addGift':
            self.get_game_state().get_state().gifts.append(event.gift)

    def game_state_event(self, event):
        self.get_game_state().set_game_loc(event)

    def pickup_event(self, event):
        if event.action == u'add' and event.pickups:
            self.get_game_state().add_pickups(event.pickups)

    def cook_event(self, event):
        go = self.get_game_state().get_object_by_id(event.objId)
        if not go:
            return
        if event.action == u'start':
            go.jobEndTime = event.jobEndTime
        go.recipeNo = event.recipeNo

    def time_gain_event(self, event):
        go = self.get_game_state().get_object_by_id(event.objId)
        if not go:
            return

        if hasattr(go, 'gainTime') and go.gainTime and \
                self.get_timer().has_elapsed(go.gainTime):
            go.materials += 1
            go.gainTime = None

        go.started = event.action == 'start'

    def plant_event(self, event):
        go = self.get_game_state().get_object_by_id(event.objId)

        if not go:
            return

        go.fertilized = True
        go.jobFinishTime = event.jobFinishTime
        go.jobStartTime = event.jobStartTime

    def game_event(self, event):
        next_play_date = event.nextPlayDate
        extra_id = event.extraId
        obj_id = event.objId
        go = self.get_game_state().get_object_by_id(obj_id)

        if not go:
            return

        go.nextPlayTimes.__setattr__(extra_id, next_play_date)
        building = self.get_item_reader().get(go.item)
        for game in building.games:
            if game.id == extra_id:
                game_prize = None
                if hasattr(event.result, 'pos'):
                    prize_pos = event.result.pos
                    game_prize = game.prizes[prize_pos]
                elif hasattr(event.result, 'won'):
                    prize_pos = event.result.won
                    if prize_pos is not None:
                        game_prize = game.combinations[prize_pos].prize
                else:
                    return

                if game_prize:
                    prize_item = game_prize.item
                    prize = self.get_item_reader().get(prize_item)
                    count = game_prize.count
                    logger.info(u'Вы выиграли %s %i шт' % (prize.name, count))

                    if prize_item == u'@COINS':
                        self.get_game_state().get_state().gameMoney += count
                    elif prize_item == u'@XP':
                        self.get_game_state().get_state().experience += count
                    elif prize_item == u'@CASH':
                        self.get_game_state().get_state().cashMoney += count
                    elif u'collection' in prize.type:
                        self.get_game_state().add_collection_item(prize.id, count)
                    else:
                        self.get_game_state().add_storage(prize_item, count)
                else:
                    logger.info(u'Вы ничего не выиграли')

    def gain_material_event(self, event):

        go = self.get_game_state().get_object_by_id(event.objId)
        if not go:
            return

        if go.doneCounter != event.doneCounter or go.startCounter != event.startCounter:
            go.doneCounter = event.doneCounter
            go.startCounter = event.startCounter

            if event.action == u'start':
                if go.target:
                    target = self.get_game_state().get_object_by_id(event.targetId)
                    target.materialCount -= 1
                    target_obj = self.get_item_reader().get(target.item)
                    go.materials.append(target_obj.material)
                    if not target.materialCount:
                        logger.info(u'Полностью вырубили %s' % target_obj.name)
                        if hasattr(target_obj, 'box'):
                            box_obj = self.get_item_reader().get(target_obj.box)
                            new_obj = dict2obj({
                                'item': target_obj.box,
                                'type': 'pickup',
                                'id': target.id,
                                'x': target.x,
                                'y': target.y
                            })
                            self.get_game_state().remove_object_by_id(target.id)
                            self.get_game_state().append_object(new_obj)
                            logger.info(u'%s превращён в %s' % (target_obj.name, box_obj.name))
                        else:
                            self.get_game_state().remove_object_by_id(target.id)

                        go.target = None
                else:
                    # Если это новое дерево, то зомбику нужно поставить что он его рубит,
                    # но эти данные обновятся и так при смене острова
                    go.target = dict2obj({'id': event.targetId})
                    target = self.get_game_state().get_object_by_id(event.targetId)
                    target.gainStarted = True

                # Зомбики продолжают работать
                go.jobStartTime = event.jobStartTime
                go.jobEndTime = event.jobEndTime

            else:
                # Закончили вырубку, освободили мозги и ушли спать
                go.target = None

    def daily_bonus_event(self, event):
        daily_bonus = event.dailyBonus
        self.get_game_state().get_state().dailyBonus.playFrom = daily_bonus.playFrom

        logger.info(u'Крутим ежедневную рулетку. День %i' % (daily_bonus.current + 1))

    @staticmethod
    def action_event(event):
        if event.action == u'sendOk':
            # Считаем что отправка прошла успешно и ничего не делаем
            pass
        else:
            pass

    def buried_event(self, event):
        if event.action == u'buried':
            # Если мы закопали
            if event.slot >= 0:
                bury_slot = self.get_game_state().get_state().burySlots[event.slot]
                bury_slot.user = event.user
                bury_slot.buriedUntil = u'22500000'

                for x in self.get_game_state().get_players():
                    if x.id == event.user:
                        x.buried = u'22500000'

                friend = self.get_game_state().get_player(event.user)
                user_name = friend.name if hasattr(friend, 'name') else event.user
                logger.info(u'Получили мозг %s %i шт ' % (user_name, 1))

            # Если мы откопали
            else:
                for x in self.get_game_state().get_players():
                    if x.id == event.user and hasattr(x, 'buried'):
                        x.__delattr__(u'buried')
        else:
            # {'buriedUntil': u'22500000', u'enabled': True, 'user': u'215620917'}
            pass

    def buyed_brains_event(self, event):
        buyed_brain = dict2obj({'count': event.brains.count, 'endTime': event.brains.endTime})
        self.get_game_state().get_state().buyedBrains.append(buyed_brain)

    def bridge_event(self, event):
        # Срабатывает когда открыли чемодан
        pass

    def players_info_event(self, event):
        players = event.players

        if self.get_params().show_away_zombiefarm_players:

            # Максиммальное время отсутствия, не может быть больше 24 суток
            deadline = 24
            day_timestamp = 1000 * 60 * 60 * 24
            deadline_timestamp = deadline * day_timestamp

            pre_aways = [x for x in players if hasattr(x, u'accessDate')]
            aways = [x for x in pre_aways if abs(int(x.accessDate)) > deadline_timestamp]

            for away_player in aways:
                logger.info(u'http://vk.com/id%s (%i дней не заходил на ферму)' %
                            (away_player.id, abs(int(away_player.accessDate)) / day_timestamp))

        saved_players = self.get_game_state().get_players()
        saved_players += players
        self.get_game_state().set_players(saved_players)

    def unblock_event(self, event):
        # Срабатывает когда нет мозга у зомби и он не может начать добычу ресурса
        resource = self.get_game_state().get_object_by_id(event.objId)
        resource.gainStarted = False

    def game_object_event(self, event):

        if event.action == u'changeObject':
            event_go = event.gameObject

            go = self.get_game_state().get_object_by_id(event_go.id)
            if not go:
                return

            go.endDate = event_go.endDate
            go.state = event_go.state
            go.users = event_go.users

    def mission_event(self, event):
        if event.action == u'getMissions':
            missions = []
            for x in event.missions:
                if x.type in [u'gameMission']:
                    missions.append(x)

            self.get_game_state().set_missions(missions)
