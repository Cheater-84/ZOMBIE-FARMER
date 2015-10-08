# -*- coding: utf-8 -*-

import random
import logging
import time
import vk

from engine.helpers import timestamp_to_str
from vk.message_factory import Session, Factory
from game_event import dict2obj, obj2dict
from game_types import GameEVT, GameTIME
from engine.item_reader import GameItemReader
from statistic.statistic import StatisticAccess

logger = logging.getLogger(__name__)

items_filename = u'items.dat'


class GameClient(object):

    def __init__(self, site, account, arg_params):
        self.site = site
        self.account = account
        self.params = account.params()
        self.arg_params = arg_params

        self.game_item_reader = None
        self.game_state = None
        self.api = None
        self.game_events_sender = None
        self.timer = None
        self.statistic = None

    def initialize(self):
        ge = GameEngine(self.site, self.account)
        ge.start()

        self.game_item_reader = ge.game_item_reader
        self.game_state = ge.game_state
        self.api = ge.api
        self.game_events_sender = ge.game_events_sender
        self.timer = ge.timer
        self.statistic = ge.statistic


class GameEngine(object):

    CLIENT_VERSION = 1385060115L
    
    def __init__(self, site, account):
        self.site = site
        self.account = account
        
        self.api_user_id = None
        self.api_access_token = None
        self.request_sender = None
        self.factory = None
        self.game_item_reader = None
        self.game_state = None
        self.connection = None
        self.session = None
        self.api = None
        self.game_events_sender = None
        self.timer = None
        self.statistic = None
        
    def start(self):
        
        logger.info(u'Обновляем файл %s...' % items_filename)
        self.game_item_reader = GameItemReader()
        self.game_item_reader.download(items_filename)
        self.game_item_reader.read(items_filename)

        logger.info(u'Логинимся...')
        self.api_user_id, game_auth_key, self.api_access_token, self.connection = self.site.get_game_params()
        self.session = Session(self.api_user_id, game_auth_key, client_version=self.CLIENT_VERSION)
        self.factory = Factory(self.session, None)
        self.request_sender = RequestSender(self.factory, self.connection)
        self.timer = GameTimer()
        
        logger.info(u'Получаем ключ сессии...')
        key = self.site.get_time_key()
        command = GameTIME(key=key)
        time_response = self.request_sender.send(command)
        server_time = time_response.time
        session_key = time_response.key
        
        logger.info(u'Синхронизируем время сервера...')
        client_time = self.timer.get_client_time()
        start_time = time.time()
        command = self.site.create_start_command(server_time, client_time)
        sending_time = (time.time() - start_time) * 1000
        self.timer.client_time += sending_time

        logger.info(u'Загружаем игровые данные...')
        self.factory.set_request_id(server_time)
        self.factory.set_session_key(session_key)
        self.factory.set_master(self.account)

        start_response = self.request_sender.send(command)  
        self.game_state = GameState(start_response, self.game_item_reader)
        self.game_events_sender = GameEventsSender(self.request_sender)
        self.api = vk.api.API(token=self.api_access_token)

        # Получаем доступ к статистике
        self.statistic = StatisticAccess(self.account)

        # Показываем нашу игровую статистику
        self.show_game_stats()
        
    def show_game_stats(self):

        buyed_brains = 0
        for buyed_brain in self.game_state.get_state().buyedBrains:
            buyed_brains += buyed_brain.count

        logger.info(u'%s КРАТКАЯ ИНФОРМАЦИЯ %s' % (u'*' * 18, u'*' * 18))

        logger.info(u'Аккаунт: %s' % self.account.user_name)
        logger.info(u'Монеты: %i' % self.game_state.get_state().gameMoney)
        logger.info(u'Зомбаксы: %i' % self.game_state.get_state().cashMoney)
        logger.info(u'Опыт: %i' % self.game_state.get_state().experience)
        logger.info(u'Уровень: %i' % self.game_state.get_state().level)
        logger.info(u'Мозги: %i (%i/%i закопанных и %i платных)' %
                    (self.game_state.get_state().brainsCount +
                     len([x for x in self.game_state.get_state().burySlots if x.enabled and
                          hasattr(x, u'user')]) + buyed_brains,
                     len([x for x in self.game_state.get_state().burySlots if x.enabled and
                          hasattr(x, u'user')]),
                     len([x for x in self.game_state.get_state().burySlots if x.enabled]),
                     buyed_brains))

        logger.info(u'Остров: %s' %
                    self.game_item_reader.get(self.game_state.get_state().locationId).name)

        for show_item in self.account.params().show_count_on_start:
            show_item_obj = self.game_item_reader.get(show_item)
            if show_item_obj.type == u'collection':
                logger.info(u'%s: %i шт' %
                            (show_item_obj.name, self.game_state.count_collection(show_item_obj.items)))
            elif show_item_obj.type == u'collectionItem':
                logger.info(u'%s: %i шт' %
                            (show_item_obj.name, self.game_state.count_collection_item(show_item)))
            else:
                logger.info(u'%s: %i шт' % (show_item_obj.name, self.game_state.count_storage(show_item)))
        for buff in self.game_state.get_state().buffs.list:
            buff_obj = self.game_item_reader.get(buff.item)
            if buff.expire.type == u'time' and int(buff.expire.endDate) > 0:
                logger.info(u'%s: %s' % (buff_obj.name, ' '.join(timestamp_to_str(int(buff.expire.endDate)))))

        logger.info(u'*' * 56)


class GameTimer(object):

    def __init__(self):
        self.client_time = 0
        self.start_time = 0

    def get_client_time(self):
        random.seed()
        self.client_time = long(random.randrange(2800, 4000))
        self.start_time = time.time()
        return self.client_time

    def get_current_client_time(self):
        current_time = self.client_time
        current_time += (time.time() - self.start_time) * 1000
        return current_time

    def has_elapsed(self, time_, correct=0):
        return self.get_current_client_time() > (int(time_) + correct * 1000)


class GameEventsSender(object):
    def __init__(self, request_sender):
        self.events_to_handle = []
        self.request_sender = request_sender

    def get_game_events(self):
        return self.events_to_handle

    def clear_game_events(self):
        self.events_to_handle = []

    def send_game_pack_events(self, events=None):
        res = []
        while events:
            res += self.send_game_events(events[:1000])
            events = events[1000:]
        return res

    def send_game_events(self, events=None):
        command = GameEVT(events=events)
        game_response = self.request_sender.send(command)
        curr_evts = [evt for evt in game_response.events if evt.type not in [u'evt', u'gameMission']]
        self.events_to_handle += curr_evts
        return curr_evts

    def remove_game_event(self, event):
        if event in self.events_to_handle:
            self.events_to_handle.remove(event)


class RequestSender(object):
    def __init__(self, message_factory, connection):
        self.factory = message_factory
        self.connection = connection

    def send(self, data):
        data = obj2dict(data)
        assert 'type' in data
        request = self.factory.create_request(data)
        return dict2obj(request.send(self.connection))

    def set_url(self, url):
        self.connection.set_url(url)

    def clear_session(self):
        self.factory.set_session_key(None)

    def set_auth_key(self, auth_key):
        self.factory.set_auth_key(auth_key)


class GameState(object):

    def __init__(self, start_response, item_reader):
        self.item_reader = item_reader
        self.state = start_response.state
        self.id_response = long(start_response.id)
        self.game_loc = None

        self.players = []
        self.players_dict = {}
        self.remote_stop = False
        self.remote_loc = None
        self.id_response = long(start_response.id)
        self.signals = {}
        self.pickups = []
        self.missions = []
        self.players_location = None
        self.current_user_id = None

        self.set_game_loc(start_response.params.event)

    def set_players_location(self, res):
        self.players_location = res

    def get_players_location(self, player):
        return self.players_location.get(player, u'main')

    def get_game_objects(self):
        return self.state.gameObjects

    def get_storage_items(self):
        return self.state.storageItems

    def get_storage_objects(self):
        return self.state.storageGameObjects

    def get_collection_items(self):
        return self.state.collectionItems

    def get_pickups(self):
        return self.pickups

    def add_pickups(self, pickups):
        self.pickups += pickups

    def clear_pickups(self):
        self.pickups = []

    def remove_pickup(self, pickup):
        self.pickups.remove(pickup)

    def get_objects_by_types(self, types):
        objects = []
        for game_object in self.get_game_objects():
            if game_object.type in types:
                objects.append(game_object)
        return objects

    def get_objects_by_items(self, items):
        objects = []
        for game_object in self.get_game_objects():
            if game_object.item in items:
                objects.append(game_object)
        return objects

    def get_object_by_id(self, obj_id):
        for game_object in self.get_game_objects():
            if game_object.id == obj_id:
                return game_object
        return None

    def remove_object_by_id(self, obj_id):
        for game_object in self.get_game_objects():
            if game_object.id == obj_id:
                self.get_game_objects().remove(game_object)
                return

    def append_object(self, obj):
        self.state.gameObjects.append(obj)

    def set_game_loc(self, game_state_event):
        self.game_loc = game_state_event.location

        for attr, val in game_state_event.__dict__.iteritems():
            self.state.__setattr__(attr, val)

    def get_game_loc(self):
        return self.game_loc

    def set_remote_loc(self, game_state_event):
        self.remote_loc = game_state_event

    def get_remote_loc(self):
        return self.remote_loc

    def get_state(self):
        return self.state

    def set_state(self, game_state):
        self.state = game_state

    def add_collection_item(self, item, count):
        item_name = item[1:] if item[:1] == '@' else item
        coll_items = self.get_collection_items()
        coll_count = obj2dict(coll_items).get(item_name, 0) + count
        self.get_state().collectionItems.__setattr__(item_name, coll_count)

    def add_collection(self, items, delta):
        for item in items:
            self.add_collection_item(item, delta)
        return True

    def count_collection(self, items):
        res = []
        for item in items:
            count = self.count_collection_item(item)
            res.append(count)
        return min(res)

    def count_collection_item(self, item):
        item_name = item[1:] if item[:1] == '@' else item
        if hasattr(self.get_collection_items(), item_name):
            return getattr(self.get_collection_items(), item_name)
        return 0

    def remove_collection(self, items, delta):
        for item in items:
            self.remove_collection_item(item, delta)
        return True

    def remove_collection_item(self, item_id, delta):
        item_name = item_id[1:] if item_id[:1] == '@' else item_id
        if hasattr(self.get_collection_items(), item_name):
            count = getattr(self.get_collection_items(), item_name)
            setattr(self.get_collection_items(), item_name, count - delta)

    def count_storage(self, item_id):
        for itemid in self.get_storage_items():
            if hasattr(itemid, 'item') and itemid.item == item_id:
                return itemid.count
        return 0

    def count_storage_object(self, item_id):
        for itemid in self.get_storage_objects():
            if hasattr(itemid, 'item') and itemid.item == item_id:
                return itemid.count
        return 0

    def remove_storage(self, item_id, count):
        for itemid in self.get_storage_items():
            if hasattr(itemid, 'item') and itemid.item == item_id:
                itemid.count -= count

    def add_storage(self, item_id, count):
        for itemid in self.get_storage_items():
            if hasattr(itemid, 'item') and itemid.item == item_id:
                itemid.count += count
                return
        item_obj = dict2obj({
            u'item': item_id,
            u'count': count
        })
        self.state.storageItems.append(item_obj)

    def get_players(self):
        return self.players

    def set_players(self, players):
        self.players = players

        for player in players:
            self.players_dict[player.id] = player

    def get_player(self, player_id):
        return self.players_dict.get(player_id, {})

    def set_missions(self, missions):
        self.missions = missions

    def get_missions(self):
        return self.missions

    def set_current_user(self, user_id):
        self.current_user_id = user_id

    def get_current_user(self):
        return self.current_user_id

    def exclude_user_id(self):
        user_id = self.get_current_user().id
        players = [x for x in self.get_players() if x.id != user_id]
        self.set_players(players)

    def set_remote_stop(self, value):
        self.remote_stop = value

    def get_remote_stop(self):
        return self.remote_stop

    def get_signal(self, key):
        return self.signals.get(key)

    def set_signal(self, key, value):
        self.signals[key] = value

    def add(self, item_obj, count):
        if item_obj.type == u'collectionItem':
            self.add_collection_item(item_obj.item, count)
        elif item_obj.type == u'collection':
            self.add_collection(item_obj.items, count)
        elif item_obj.type == u'storage':
            self.add_storage(item_obj.item, count)

    def remove(self, item_obj, count):
        if item_obj.type == u'collectionItem':
            self.remove_collection_item(item_obj.item, count)
        elif item_obj.type == u'collection':
            self.remove_collection(item_obj.items, count)
        elif item_obj.type == u'storage':
            self.remove_storage(item_obj.item, count)

    def count(self, item_obj):
        if item_obj.type == u'collectionItem':
            self.count_collection_item(item_obj.item)
        elif item_obj.type == u'collection':
            self.count_collection(item_obj.items)
        elif item_obj.type == u'storage':
            self.count_storage(item_obj.item)
