# -*- coding: utf-8 -*-

import json
import collections
import random
import logging
import urllib2
import hashlib
import sys

logger = logging.getLogger(__name__)

url = None


class Session(object):
    def __init__(self, user_id, auth_key, client_version=1406282412, session_key=None):
        self.__user_id = user_id          # vk user id
        self.__session_key = session_key  # session key from TIME request
        self.__auth_session_key = None    # key from TIME response
        self.__auth_key = auth_key        # auth key from vk.com flashvars
        self.__client_version = client_version

    def get_user_id(self):
        return self.__user_id

    def get_session_key(self):
        return self.__session_key

    def set_session_key(self, session_key):
        self.__session_key = session_key

    def get_auth_key(self):
        return self.__auth_key

    def set_auth_key(self, auth_key):
        self.__auth_key = auth_key

    def get_auth_session_key(self):
        return self.__auth_session_key

    def get_client_version(self):
        return self.__client_version


class Factory(object):
    def __init__(self, session, base_request_id=None):
        
        base_request_id = self.get_initial_id() if base_request_id is None else base_request_id
        
        self.__session = session
        self.__request_id = base_request_id
        self.parsed_salt = None
        self.master = None

    @staticmethod
    def get_initial_id():
        random.seed()
        return random.randrange(40, 60)

    def set_request_id(self, request_id):
        self.__request_id = request_id

    def get_request_id(self):
        return self.__request_id

    def inc_request_id(self):
        self.__request_id += 1

    def get_session(self):
        return self.__session

    def get_session_key(self):
        return self.get_session().get_session_key()

    def set_session_key(self, session_key):
        self.get_session().set_session_key(session_key)

    def set_auth_key(self, auth_key):
        self.get_session().set_auth_key(auth_key)

    def set_master(self, master):
        self.master = master

    def create_request(self, data, data_keys_order=None):
        data = self.create_data_value(data, data_keys_order)
        crc = self.generate_crc(data)
        return Request(dict(data=data, crc=crc))

    @staticmethod
    def md5hash(string):
        m = hashlib.md5()
        m.update(string.encode(u'utf-8'))
        return m.hexdigest()

    def salt_function(self, string):
        result = str(len(string)) + self.md5hash(string + 'stufff...')
        salt13 = str(len(string) * 17 + 13)
        salt2 = self.md5hash(salt13 + str(len(string)) + str(len(salt13)))
        result += salt2
        character_sum = 0
        for i in xrange(len(string)):
            character_sum += (ord(string[i]) & 250)
        result += str(character_sum)
        return result

    def generate_crc(self, string):
        return self.md5hash(string + self.salt_function(string))

    def generate_sig(self, session_key, request_id, auth_key, parsed_salt):
        sig = session_key + str(request_id) + auth_key
        salt = sig

        for letter in parsed_salt:
            if letter == '1':
                salt += salt
            elif letter == '2':
                salt = salt.replace('0', '1')
            elif letter == '3':
                salt = salt[:len(salt)/2]
            elif letter == '4':
                salt = salt[::-1]
            elif letter == '5':
                salt = str(len(salt) * 13)
            elif letter == '6':
                salt = salt.upper()
            elif letter == '7':
                salt = salt.lower()
            elif letter == '8':
                salt += 's.shadowlands.ru/zombievk-res/'

        sig += salt
        sig = self.md5hash(sig)
        return sig

    def generate_auth(self, request_id, auth_key):
        auth = str(request_id) + auth_key
        auth += self.salt_function(auth)
        sig = self.md5hash(auth)
        return sig

    def create_data_value(self, data, data_keys_order):

        if not data_keys_order:
            message_types = {
                'TIME': ['auth', 'type', 'clientVersion', 'user',  'id', 'key'],
                'START': ['id',  'sig', 'clientTime', 'serverTime', 'info', 'type', 'user', 'ad', 'lang'],
                'EVT': ['user', 'type', 'id', 'sig', 'events']
            }
            data_keys_order = message_types.get(data['type'], [])
        
        datacopy = data.copy()
        datacopy['user'] = str(self.get_session().get_user_id())
        datacopy['id'] = self.get_request_id()
        datacopy['sig'] = ''
        datacopy['auth'] = ''
        datacopy['clientVersion'] = self.get_session().get_client_version()
        
        data_value = collections.OrderedDict()
        for key in data_keys_order:
            if key in datacopy:
                data_value[key] = datacopy[key]
        
        if data['type'] == 'START':
            info_keys = ['uid', 'bdate', 'country', 'first_name', 'sex', 'city', 'last_name']
            data_value['info'] = collections.OrderedDict()
            for info_key in info_keys:
                if info_key in datacopy['info']:
                    data_value['info'][info_key] = datacopy['info'][info_key]

        self.add_sig_or_auth(data_value)
        self.inc_request_id()

        return json.dumps(data_value, separators=(',', ':'), ensure_ascii=False, encoding='utf-8')

    def add_sig_or_auth(self, object_data):

        session_key = self.get_session().get_session_key()
        auth_key = self.get_session().get_auth_key()
        auth_session_key = self.get_session().get_auth_session_key()

        if session_key is not None:
            if not self.parsed_salt:
                logger.info(u'Получаем ключ авторизации...')

                server = url.split('.')[0][11:]
                ss_key = session_key[session_key.find(':') + 1:]
                request = urllib2.Request('http://%s:%s/salt?session_key=%s&server=%s&private_key=%s' %
                                          (self.master.ip_address, self.master.port, ss_key, server,
                                           self.master.private_key))
                req_handler = urllib2.urlopen(request)
                received_data = json.loads(req_handler.read())

                if not received_data.get('salt'):
                    logger.info(received_data['error'])
                    raw_input(u'')
                    sys.exit()
                else:
                    self.parsed_salt = received_data.get('salt')

            object_data['sig'] = self.generate_sig(session_key, self.get_request_id(), auth_key, self.parsed_salt)
        
        else:
            object_data['auth'] = self.generate_auth(self.get_request_id(), auth_key)
            if auth_session_key is not None:
                object_data['key'] = auth_session_key


class Request(object):

    def __init__(self, data):
        self.__data = data

    def __str__(self):
        return str(self.__data)

    def get_data(self):
        return self.__data

    def send(self, connection):
        response = self.get_response(connection)
        if 'redirect' in response:
            global url
            url = response['redirect']
            connection.set_url(url + '/go')
        if 'cmd' in response:
            if response['cmd'] == 'REDIRECT':
                # send request again with new url
                response = self.get_response(connection)
            elif response['cmd'] == 'ERR':
                error_msg = response['msg']
                raise GameError(u'Ошибка ключа: ' + error_msg)
        return response

    def get_response(self, connection):
        return Response(connection.send_request(self.get_data())).get_dict()


class GameError(Exception):
    pass


class Response(object):
    def __init__(self, response_string):
        if '$' in response_string:
            crc, response = response_string.split('$', 1)
        else:
            response = response_string
        self.__response = json.loads(response)

    def get_dict(self):
        return self.__response
