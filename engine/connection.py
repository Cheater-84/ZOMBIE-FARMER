# encoding=utf-8
import urllib
import urllib2
import StringIO
import gzip
import Cookie
import logging
import time

logger = logging.getLogger(u'connection')


class Connection(object):
    def __init__(self, url):
        self.__url = url

    def set_url(self, new_url):
        self.__url = new_url

    def get_changed_document(self, last_client_time=None, data=None):
        modified_headers = None
        if last_client_time:
            time_format = '%a, %d %b %Y %H:%M:%S %Z'
            last_client_time = time.strftime(time_format, last_client_time)
            modified_headers = [(u'If-Modified-Since', last_client_time)]
        response = self.get_response(data, modified_headers)
        if not response:
            return None
        if response.getcode() != 304:
            logger.info(u'document modified, downloading...')
            return self.read_content(response)
        else:
            return None

    def get_response(self, data, cookies=None, headers=None):
        opener = urllib2.build_opener()
        opener.addheaders = self.get_headers().items()
        if headers is not None:
            opener.addheaders += headers
        if cookies is not None:
            opener.addheaders += [(u'Cookie', cookies)]
        if data is not None:
            data = urllib.urlencode(self.encode_dict(data))
        logger.info(u'request: ' + self.__url + ' ' + str(data))
        try:
            response = opener.open(self.__url, data, timeout=30)
        except urllib2.HTTPError, e:
            logger.error(u'HTTP error:' + unicode(e.message))
            response = None
        return response

    def send_request(self, data=None, cookies=None, get_cookies=False, get_content=False):
        response = self.get_response(data, cookies)
        if response:
            content = self.read_content(response)
            response.close()
            logger.info(u'response: ' + content)
            if get_cookies:
                if get_content:
                    return Cookie.SimpleCookie(response.info().get('Set-Cookie')), content
                else:
                    return Cookie.SimpleCookie(response.info().get('Set-Cookie'))
            else:
                return content

    @staticmethod
    def read_content(response):
        encoding = response.headers.getparam(u'charset')
        if response.info().get(u'Content-Encoding') == u'gzip':
            buf = StringIO.StringIO(response.read())
            gzip_f = gzip.GzipFile(fileobj=buf)
            content = gzip_f.read()
        else:
            content = response.read()
        content = content.decode(encoding)
        return content

    @staticmethod
    def encode_dict(params):
        return dict([(key, val.encode(u'utf-8')) for key, val in params.items() if isinstance(val, basestring)])

    @staticmethod
    def get_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0',
            'Host': '95.163.80.22',
            'Connection': 'keep-alive',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
