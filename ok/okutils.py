# encoding=utf-8

import sys
from engine.connection import Connection
from ok import api
import requests
import re
from engine.game_types import GameSTART, GameInfo
from hashlib import md5

sys.path.append('./API')


class OK(object):
    def __init__(self, credentials):
        self._credentials = credentials
        self._params = None
        self._ok_user_id = None

    def str2dict(self, val):
        if type(val) is str:
            res = {}
            for tmp in val.replace(' ', '').split(';'):
                k = tmp.split('=')[0]
                v = tmp.split('=')[1]
                res[k] = v
            return res
        else:
            return val

    def getAppParams(self, session_cookies=None):
        if session_cookies is None:
            session_cookies = self._get_session_cookies()

        #html = requests.get('http://www.ok.ru/games/zm', cookies=self.str2dict(session_cookies)).text
        ''' ссылка в одноклассниках меняется раз в неделю меняется именно этот ключ - gwt.requested=57e6afc1'''
        html = requests.get('http://ok.ru/game/zm?st.cmd=appMain&st.appId=625920&gwt.requested=57e6afc1&p_sId=0', cookies=self.str2dict(session_cookies)).text
        params = None
        if html:
            matcher = re.compile('.*zombiefarm.html\?(.*?)"')
            for line in html.split('\n'):
                match = matcher.match(line)
                if match is not None:
                    params = match.group(1)
                    break
            if params is not None:
                pairs = params.split('&amp;')
                params = {}
                for pair in pairs:
                    key = pair.split('=')[0]
                    value = pair.split('=')[1]
                    params[key] = value
        return params

    def get_game_params(self):

        params = self.getAppParams()
        ok_user_id = params['logged_user_id']
        ok_auth_key = params['auth_sig']
        ok_session_key = params['session_secret_key']
        game_url = 'http://jok.shadowlands.ru/zombieok/go'
        connection = Connection(game_url)
        self._params = params
        self._ok_user_id = ok_user_id
        return ok_user_id, ok_auth_key, ok_session_key, connection

    def get_time_key(self):
        del self._params['sig']
        return self._params['session_key']

    def create_start_command(self, server_time, client_time):
        command = GameSTART(lang=u'ru', info=self._getUserInfo(), ad=u'search', serverTime=server_time,
                            clientTime=client_time)
        return command

    def _getUserInfo(self):
        post = {
            'uids': self._params['logged_user_id'],
            'new_sig': 1,
            'session_key': self._params['session_key'],
            'fields': u'uid,first_name,last_name,gender,birthday,locale,location',
            'application_key': self._params['application_key'],
            'format': 'Json'
        }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), api._encode(post[key])) for key in post_keys])
        param_str += self._params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
        info = requests.post('http://api.ok.ru/api/users/getInfo', data=post).json()[0]

        game_info = GameInfo(city=info['location']['city'], first_name=info['first_name'], last_name=info['last_name'],
                             uid=long(info['uid']), country=info['location']['country'], bdate=info['birthday'])
        global uid
        uid = info['uid']
        return game_info

    def _get_friend_info(self, friend):
        post = {
            'uids': friend,
            'new_sig': 1,
            'session_key': self._params['session_key'],
            'fields': u'uid,first_name,last_name,gender,birthday,locale,location',
            'application_key': self._params['application_key'],
            'format': 'Json'
        }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), api._encode(post[key])) for key in post_keys])
        param_str += self._params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
        info = requests.post('http://api.ok.ru/api/users/getInfo', data=post).json()[0]
        print info

    def _get_friends_list(self):
        post = {
            'new_sig': 1,
            'session_key': self._params['session_key'],
            'application_key': self._params['application_key'],
            'format': 'Json'
        }
        post_keys = sorted(post.keys())
        param_str = "".join(["%s=%s" % (str(key), api._encode(post[key])) for key in post_keys])
        param_str += self._params['session_secret_key']
        sign = md5(param_str).hexdigest().lower()
        post.update({'sig': sign})
        info = requests.post('http://api.ok.ru/api/friends/getAppUsers', data=post).json()['uids']

        return info

    def _validate_session_cookies(self, session_cookies):
        if session_cookies is not None:
            return self.getAppParams(session_cookies) is not None
        return False

    def _get_session_cookies(self):
        username = self._credentials.user_login
        password = self._credentials.user_password
        post = {
            'st.posted': 'set',
            'st.redirect': '%2Fgames%2Fzm',
            'st.originalaction': u'http://www.ok.ru/dk?cmd=AnonymLogin&st.cmd=anonymLogin',
            'st.fJS': 'enabled',
            'st.email': username,
            'st.password': password,
            'st.remember': 'on',
            'button_go': 'Sign in'
        }

        sslurl = requests.post('https://www.ok.ru/https', data=post, allow_redirects=False, verify=True)
        sslurl_headers_location = sslurl.headers['location']
        session_cookies = requests.get(sslurl_headers_location, allow_redirects=False).cookies

        return session_cookies

    def getFriends(self):
        return self.friendsid

    def getMyId(self):
        return self._params['logged_user_id']
