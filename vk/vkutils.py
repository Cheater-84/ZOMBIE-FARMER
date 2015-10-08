# -*- coding: utf-8 -*-

import re
import json

from vk.api import API
from engine.connection import Connection
from engine.game_types import GameSTART, GameInfo


class VK(object):
    def __init__(self, credentials):
        self.credentials = credentials
        self.game_api_user_id = None
        self.api_access_token = None

    def get_app_params(self, app_id, session_cookies=None):
        if session_cookies is None:
            session_cookies = self.get_session_cookies()
        vk = Connection(u'https://vk.com/app' + str(app_id))
        html = vk.send_request(None, cookies=session_cookies)
        params = None
        if html:
            matcher = re.compile(r'.*var params = (.*);$')
            for line in html.split(u'\n'):
                match = matcher.match(line)
                if match is not None:
                    params = match.group(1)
                    break
            if params is not None:
                return json.loads(params)

        return params

    def get_game_params(self):
        params = self.get_app_params(u'612925')
        self.game_api_user_id = params['viewer_id']
        game_auth_key = params['auth_key']
        self.api_access_token = params['access_token']
        game_url = 'http://java.shadowlands.ru/zombievk/go'
        connection = Connection(game_url)
        return self.game_api_user_id, game_auth_key, self.api_access_token, connection

    @staticmethod
    def get_time_key():
        return None

    def create_start_command(self, server_time, client_time):
        command = GameSTART(lang=u'en', info=self.get_user_info(), ad=u'user_apps', serverTime=server_time,
                            clientTime=client_time)
        return command

    def get_user_info(self):

        api = API(token=self.api_access_token)
        info = api.getProfiles(uids=self.game_api_user_id, format='json', fields='bdate,sex,first_name,last_name')
        info = info[0]
        bdate = info['bdate'] if 'bdate' in info else None

        game_info = GameInfo(first_name=info['first_name'], last_name=info['last_name'],
                             uid=long(info['uid']), sex=long(info['sex']), bdate=bdate)
        return game_info

    def get_session_cookies(self):
        username = self.credentials.user_login
        password = self.credentials.user_password
        post = {
            'act': 'login',
            'role': 'al_frame',
            'expire': '',
            'captcha_sid': '',
            'captcha_key': '',
            '_origin': 'http://vk.com',
            'email': username,
            'pass': password
        }

        vk = Connection('http://vk.com/')
        session_cookies, html = vk.send_request(data=None, get_cookies=True, get_content=True)
        session_cookies = ('Cookie:' + session_cookies.output(attrs=[], header='', sep=';'))
        if html:
            matcher = re.compile(r'<input type="hidden" name="([^"]+)" value="([^"]*)" />')
            post.update(dict(matcher.findall(html)))

        vk = Connection('https://login.vk.com/?act=login')
        session_cookies = vk.send_request(post, get_cookies=True, cookies=session_cookies)
        session_cookies = ('Cookie:' + session_cookies.output(attrs=[], header='', sep=';'))

        return session_cookies
