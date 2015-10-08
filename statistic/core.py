# -*- coding: utf-8 -*-

import os
import logging
from sqlite3 import connect
from vk.message_factory import GameError
from engine.game_types import GameGetInfo, ChangeLocation
from engine.base import Core

logger = logging.getLogger(__name__)


class StatisticCore(Core):

	def __init__(self, game):

		super(StatisticCore, self).__init__(game)

		self.db_name = '%s/params/db/stat_%s.db' % (os.getcwd(), game.account.user_name)
		self.conn = connect(self.db_name)
		self.cursor = self.conn.cursor()

		self.status_enum = {
			'NOT_CHECKED': 0, 'NOT_OPEN': 1, 'OPENED': 2, 'PLATFORM': 3, 'VALRIGHT': 4, 'JAPAN': 5, 'HYPER': 6, 'FISHER': 7
		}

	def create(self):

		island_ids = []
		values_ids = []
		for island in self.get_game().params.statistic_islands:
			island_ids.append(u'%s int' % island)
			values_ids.append(u'0')

		isle_pattern = u', '.join(island_ids)
		values_pattern = u', '.join(values_ids)

		query = 'CREATE TABLE IF NOT EXISTS users (uid VARCHAR(20), %s)' % isle_pattern
		self.cursor.execute(query)

		self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_uid ON users (uid)')

		logger.info(u'Запрашиваем список соседей')
		friends = [unicode(x) for x in self.get_game().api.friends.getAppUsers()]

		logger.info(u'Заполняем базу соседями, которых нет в базе данных')
		while friends:
			friend = friends.pop(0)
			query = 'INSERT OR IGNORE INTO users VALUES ("%s", %s)' % (friend, values_pattern)
			self.cursor.execute(query)

		self.conn.commit()

	def parse(self):

		dependence = {
			u'isle_03': [u'isle_02', u'isle_x', u'isle_faith', u'isle_hope', u'isle_scary'],
			u'isle_x': [u'isle_faith', u'isle_hope', u'isle_scary'],
			u'isle_faith': [u'isle_scary'],
			u'isle_mobile': [u'isle_giant', u'isle_moon', u'isle_xxl'],
			u'isle_giant': [u'isle_moon', u'isle_xxl'],
			u'isle_moon': [u'isle_xxl'],
			u'isle_wild': [u'isle_star', u'isle_large'],
			u'isle_star': [u'isle_large'],
			u'isle_polar': [u'isle_small'],
			u'isle_desert': [u'isle_ufo', u'isle_dream'],
			u'isle_ufo': [u'isle_dream']
		}

		for island in self.get_game().params.statistic_islands:
			isle_obj = self.get_game().game_item_reader.get(u'@%s' % island)
			while True:
				query = 'SELECT uid FROM users WHERE %s = 0 LIMIT 100' % island
				self.cursor.execute(query)

				user_pack = [unicode(row[0]) for row in self.cursor]
				if not user_pack:
					break

				logger.info(u'Выбираем %i человек для анализа. Остров: %s' % (len(user_pack), isle_obj.name))
				get_info = GameGetInfo(players=user_pack)
				players = self.send_get_info([get_info])
				players.sort(key=lambda var_x: var_x.level, reverse=True)

				res = [x.id for x in players]
				for source_user in user_pack:
					if source_user not in res:
						self.cursor.execute('DELETE FROM users WHERE uid = "%s"' % source_user)
				self.conn.commit()

				counter = 0
				for player in players:
					try:
						if player.banned:
							self.cursor.execute('DELETE FROM users WHERE uid = "%s"' % player.id)
							continue

						if hasattr(player, 'playerStatus'):
							if player.playerStatus in [u'@PS_PRISONER']:
								self.cursor.execute('DELETE FROM users WHERE uid = "%s"' % player.id)
								continue

						res = self.status_enum.get('NOT_CHECKED')
						fisher = False
						guard = False

						change_location_event = ChangeLocation(user=player.id, locationId=island)
						remote_game_objects = self.send_change_location([change_location_event])

						res |= (1 << self.status_enum.get('OPENED'))

						for go in remote_game_objects:
							if go.item in [u'@D_PLATFORM', u'@D_PLATFORM_2']:
								res |= (1 << self.status_enum.get('PLATFORM'))

							elif go.item in [u'@D_VALRIGHT']:
								res |= (1 << self.status_enum.get('VALRIGHT'))

							elif go.item in [u'@DS_SYMBOL_E', u'@D_SYMBOL_E', u'@D_ARBOR', u'@D_JAPAN_ARBOR']:
								res |= (1 << self.status_enum.get('JAPAN'))

							elif go.item in [
								u'@SC_FISHER_GRAVE_BRAINER', u'@SC_FISHER_GRAVE',
								u'@SC_DIGGER_GRAVE_BRAINER', u'@SC_DIGGER_GRAVE'
							]:
								fisher = True

							elif go.item in [u'@SC_GUARD_GRAVE_WITH_BRAINS', u'@SC_GUARD_GRAVE']:
								guard = True

							elif go.item in [
								u'@B_ELEPHANT', u'@B_ELEPHANT_CASH', u'@D_OLYMPIAD_STATUE',
								u'@B_FLAG_OLIMPIADA', u'@D_PINKHEART2', u'@D_PINKHEART1',
								u'@D_STONEHEART2', u'@D_STONEHEART1', u'@SC_MG3', u'@SC_MG2',
								u'@SC_MG1', u'@SC_MW2', u'@SC_MW1', u'@SC_MW3', u'@SC_MB1',
								u'@SC_MB2', u'@SC_MB3', u'@SC_OAK7', u'@SC_OAK6', u'@SC_OAK5',
								u'@SC_PALM1', u'@SC_PALM2', u'@SC_PALM3', u'@SC_SEQ2', u'@SC_SEQ1'
							]:
								res |= (1 << self.status_enum.get('HYPER'))

						if fisher and not guard:
							res |= (1 << self.status_enum.get('FISHER'))

						query = 'UPDATE users SET %s = %i WHERE uid = "%s"' % (island, res, player.id)
						self.cursor.execute(query)

						counter += 1

					except GameError:
						logger.info(u'---Проверено %i из %i' % (counter, len(players)))

						response = self.get_game().api.isAppUser(uid=player.id)
						if not int(response):
							self.cursor.execute('DELETE FROM users WHERE uid = %s' % player.id)
							self.conn.commit()
							raise

						if island == u'main':
							raise

						res |= (1 << self.status_enum.get('NOT_OPEN'))
						query = 'UPDATE users SET %s = %i WHERE uid = "%s"' % (island, res, player.id)
						self.cursor.execute(query)
						for dependence_island in dependence.get(island, []):
							query = 'UPDATE users SET %s = %i WHERE uid = "%s"' % (dependence_island, res, player.id)
							self.cursor.execute(query)
						self.conn.commit()
						raise

				self.get_game().game_events_sender.clear_game_events()
				self.conn.commit()

		logger.info(u'Проверка завершена')

	def send_get_info(self, evt_list):
		evts = self.get_game().game_events_sender.send_game_events(evt_list)
		for evt in evts:
			if evt.type == u'playersInfo':
				return evt.players
		return self.send_get_info([])

	def send_change_location(self, evt_list):
		evts = self.get_game().game_events_sender.send_game_events(evt_list)
		for evt in evts:
			if evt.type == u'gameState':
				return evt.gameObjects
		return self.send_change_location([])

	def run(self):
		self.create()
		self.parse()

