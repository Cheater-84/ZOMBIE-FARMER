# -*- coding: utf-8 -*-

import socket
import traceback
import urllib2
import ssl
import time
import logging
from remote.core import RemoteCore
from tropic.core import TropicCore
from pirate.core import PirateCore
from local.core import LocalCore
from statistic.core import StatisticCore
from engine.game_client import GameClient

logger = logging.getLogger(__name__)


class Game(object):

    @staticmethod
    def run(site, account, arg_params):

        params = account.params()
        params.exclude_players = []

        while True:
            try:
                # Инициализируем бот
                game_client = GameClient(site, account, arg_params)
                game_client.initialize()

                # Запускаем бот в работу
                mode_actions = [LocalCore, RemoteCore, PirateCore, TropicCore, StatisticCore]
                mode_actions[arg_params.get('mode')](game_client).run()

            except (urllib2.HTTPError, urllib2.URLError) as e:
                seconds = 3
                if e.message:
                    logger.error(e.message)
                logger.error(u'Timeout occurred, retrying in %s seconds...' % seconds)
                time.sleep(seconds)

            except (socket.timeout, socket.error, ssl.SSLError) as e:
                seconds = 10
                if e.message:
                    logger.error(e.message)
                logger.error(u'Socket error occurred, retrying in %s seconds...' % seconds)
                time.sleep(seconds)

            except Exception as e:
                seconds = 5
                logger.error(traceback.format_exc())
                if e.message:
                    logger.error(e.message)
                logger.error(u'Retrying in %s seconds...' % seconds)
                time.sleep(seconds)
