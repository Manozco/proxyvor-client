"""
module for the parent class of proxy testers
"""
# pylint: disable=relative-import

import proxyvor.reflector_handler as reflector_handler
import urllib.request, urllib.error, urllib.parse
import proxyvor.tester_result as tester_result
import proxyvor.tools.exceptions as exceptions
import pycurl
import logging

LOGGER = logging.getLogger()


class ProxyTester(object):
    """
    parent class for testing proxys

    all derived classes must implement the test() method
    """
    # pylint: disable=too-many-arguments
    def __init__(self, ip, port, target_object, http_timeout=-1, socks_timeout=-1):
        assert isinstance(ip, str)
        assert isinstance(port, int)
        assert isinstance(target_object, reflector_handler.ReflectorHandler)

        self._ip = ip
        self._port = port
        self._target = target_object
        self._content_result = None
        self._result = None
        self._http_timeout = -1
        self._socks_timeout = -1
        if http_timeout != -1 and http_timeout > 0:
            self._http_timeout = http_timeout
        if socks_timeout != -1 and socks_timeout > 0:
            self._socks_timeout = socks_timeout

    def result(self):
        # pylint: disable=missing-docstring
        return self._content_result

    def test(self):
        """
        class to call in order to run tests
        MUST be derived
        """
        raise exceptions.NotImplementedError("You must use a subclass")


class HttpTester(ProxyTester):
    """
    class for testing http proxys
    """
    def __init__(self, ip, port, target_object):
        assert isinstance(ip, str)
        assert isinstance(port, int)
        assert isinstance(target_object, reflector_handler.ReflectorHandler)
        super(HttpTester, self).__init__(ip, port, target_object)
        self._type = 'http'
        self._token = ""
        self._content_result = None

    def test(self):
        self._token = self._target.get_token()
        proxy_handler = urllib.request.ProxyHandler({self._type: '{0}:{1}'.format(self._ip,
                                                                           self._port)})
        try:
            proxy_opener = urllib.request.build_opener(proxy_handler)
            timeout = self._http_timeout if (self._http_timeout != -1 and self._http_timeout > 0) else None
            if timeout:
                proxy_opener.open(self._target.target_url_to_reach_proxy(self._token), timeout=timeout)
            else:
                proxy_opener.open(self._target.target_url_to_reach_proxy(self._token))
        except urllib.error.URLError as urllib_error:
            LOGGER.error("Proxy Connection failed: {}".format(urllib_error.reason))
            raise exceptions.UrllibError(urllib_error)
        except Exception as base_except:
            LOGGER.error("Exception occurs: {}".format(base_except))
            raise exceptions.Error(base_except)

        try:
            no_proxy_opener = urllib.request.build_opener()
            timeout = self._http_timeout if (self._http_timeout != -1 and self._http_timeout > 0) else None
            if timeout:
                no_proxy_opener.open(self._target.target_url_to_reach_real(self._token), timeout=timeout)
            else:
                no_proxy_opener.open(self._target.target_url_to_reach_real(self._token))
        except urllib.error.URLError as urllib_error:
            LOGGER.error("Real Connection failed: {}".format(urllib_error.reason))
            raise exceptions.UrllibError(urllib_error)
        except Exception as base_except:
            LOGGER.error("Exception occurs: {}".format(base_except))
        try:
            self._result = urllib.request.urlopen(self._target.token_result_url(self._token))
        except urllib.error.URLError as urllib_error:
            LOGGER.error("Failed to get results back: {}".format(urllib_error.reason))
            raise exceptions.UrllibError(urllib_error)

        try:
            LOGGER.debug(self._result.info())
            if self._result.getcode() == 200:
                self._content_result = tester_result.ProxyResult(self._result.read())
        except AttributeError:
            LOGGER.warning("No result")
            raise exceptions.AttributeError


class SocksTester(ProxyTester):
    """
    common parent class for testing socks4 and socks5 proxys
    """
    def __init__(self, ip, port, target_object):
        assert isinstance(ip, str)
        assert isinstance(port, int)
        assert isinstance(target_object, reflector_handler.ReflectorHandler)
        super(SocksTester, self).__init__(ip, port, target_object)
        self._type = 'socks'
        self._token = ""
        self._content_result = None
        self._proxy_type = None

    def test(self):
        self._token = self._target.get_token()
        try:
            proxy_obj = pycurl.Curl()
            proxy_obj.setopt(pycurl.WRITEFUNCTION, lambda x: None)  # Don't print result on stdout
            proxy_obj.setopt(pycurl.URL, self._target.target_url_to_reach_proxy(self._token))
            proxy_obj.setopt(pycurl.PROXY, str(self._ip + ":" + str(self._port)))
            if self._socks_timeout != -1 and self._socks_timeout > 0:
                proxy_obj.setopt(pycurl.CONNECTTIMEOUT, self._socks_timeout)
            proxy_obj.setopt(pycurl.PROXYTYPE, self._proxy_type)
            proxy_obj.setopt(pycurl.SSL_VERIFYPEER, 0)
            proxy_obj.setopt(pycurl.SSL_VERIFYHOST, 0)
            proxy_obj.perform()
        except pycurl.error as pycurl_error:
            LOGGER.error("Proxy connection failed: {}".format(pycurl_error))
            raise exceptions.PyCurlError(pycurl_error)
        except Exception as base_exception:
            LOGGER.error("Unknown exception occurs: {}".format(base_exception))
            raise exceptions.Error(base_exception)

        try:
            no_proxy_obj = pycurl.Curl()
            no_proxy_obj.setopt(pycurl.WRITEFUNCTION, lambda x: None)  # Don't print result on stdout
            no_proxy_obj.setopt(pycurl.URL, self._target.target_url_to_reach_real(self._token))
            if self._socks_timeout != -1 and self._socks_timeout > 0:
                no_proxy_obj.setopt(pycurl.CONNECTTIMEOUT, self._socks_timeout)
            no_proxy_obj.setopt(pycurl.SSL_VERIFYPEER, 0)
            no_proxy_obj.setopt(pycurl.SSL_VERIFYHOST, 0)
            no_proxy_obj.perform()
        except pycurl.error as pycurl_error:
            LOGGER.error("Real connection failed: {}".format(pycurl_error))
            raise exceptions.PyCurlError(pycurl_error)
        except Exception as base_exception:
            LOGGER.error("Unknown exception occurs: {}".format(base_exception))
            raise exceptions.Error(base_exception)

        try:
            self._result = urllib.request.urlopen(self._target.token_result_url(self._token))
        except urllib.error.URLError as urllib_error:
            LOGGER.error("Failed to get results back: {}".format(urllib_error.reason))
            raise exceptions.UrllibError(urllib_error)
        LOGGER.debug(self._result.info())
        if self._result.getcode() == 200:
            self._content_result = tester_result.ProxyResult(self._result.read())


class Socks5Tester(SocksTester):
    """
    class for testing socks5 proxys
    """
    def __init__(self, ip, port, target_object):
        super(Socks5Tester, self).__init__(ip, port, target_object)
        self._type = 'socks5'
        self._proxy_type = pycurl.PROXYTYPE_SOCKS5


class Socks4Tester(SocksTester):
    """
    class for testing socks4 proxys
    """
    def __init__(self, ip, port, target_object):
        super(Socks4Tester, self).__init__(ip, port, target_object)
        self._type = 'socks4'
        self._proxy_type = pycurl.PROXYTYPE_SOCKS4
