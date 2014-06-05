"""
module for storing results
"""
import proxyvor.tools.json_wrapper as json
import proxyvor.tools.exceptions as exceptions
import logging

LOGGER = logging.getLogger()

BAD_ANONYMITY = -1
NEUTRAL = 0
GOOD_ANONYMITY = 1
BAD_HEADERS_FOR_PROXY = ["Via",
                         "X-Proxy-Id", ]


class ProxyResult(object):
    """
    class for storing the result of a test
    the result should be a json string
    if it is not, it is recommended to use another class for tests, and another class
    for storing the results
    """
    def __init__(self, result):
        assert isinstance(result, (str, unicode))

        self._result = result
        self._json_result = None
        try:
            self._json_result = json.loads(result)
        except exceptions.JsonLoadError:
            LOGGER.error('Format is invalid, can not parse')
            raise

    def __str__(self):
        try:
            return json.dumps(self._json_result,
                              sort_keys=True,
                              indent=4,
                              separators=(',', ': '))
        except exceptions.JsonDumpError:
            LOGGER.error("Can not dump result as json: {}".format(self._json_result))
            raise

    def proxy(self):
        """
        returns the proxy part of the data
        """
        return self._json_result.get('proxy', {})

    def real(self):
        """
        returns the real part of the data
        """
        return self._json_result.get('real', {})

    def real_client_ip(self):
        """
        return the real client ip
        """
        return self.real().get('client_ip', '')
