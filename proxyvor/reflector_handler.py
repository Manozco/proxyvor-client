"""
module for working with a target
"""
import proxyvor.tools.json_wrapper as json
import requests
import logging
import proxyvor.tools.exceptions as exceptions


LOGGER = logging.getLogger()


class ReflectorHandler(object):
    """
    class for working with a target
    """
    def __init__(self, target_data):
        self._target_data = target_data

    def target_data(self):
        """
        returns the json object associated to the target
        """
        return self._target_data

    def token_create_url(self):
        """
        return the url for creating a token
        """
        return "{0}:{1}/{2}".format(self._target_data['base_url'],
                                    self._target_data['base_port'],
                                    self._target_data['token_create_url'])

    def target_url_to_reach(self, token, real=False, proxy=False):
        """
        return the url for recording a connection
        """
        prefix = ""
        if real and not proxy:
            prefix = "r/"
        elif proxy and not real:
            prefix = "p/"
        return "{0}:{1}/{2}{3}".format(self._target_data['base_url'],
                                       self._target_data['base_port'],
                                       prefix,
                                       token)

    def target_url_to_reach_real(self, token):
        """
        return the url for recording a real connection
        """
        return self.target_url_to_reach(token, real=True)

    def target_url_to_reach_proxy(self, token):
        """
        return the url for recording a proxy connection
        """
        return self.target_url_to_reach(token, proxy=True)

    def token_result_url(self, token):
        """
        return the url for getting the result associated to a token
        """
        return "{0}:{1}/{2}/{3}".format(self._target_data['base_url'],
                                        self._target_data['base_port'],
                                        self._target_data['result_base_url'],
                                        token)

    def parse_token(self, request_result):
        """
        parse the return of the create token url and return the token
        """
        token = ""
        if request_result.status_code == 200:
            try:
                token = json.loads(request_result.content)[self._target_data['token_key_in_result']]
            except exceptions.JsonLoadError as value_error:
                LOGGER.warning("Cannot parse result, got error: {}".format(value_error))
                raise
        return token

    def get_token(self):
        """
        do the request and return the token
        """
        token = ""
        try:
            token = self.parse_token(requests.put(self.token_create_url(), {}, verify=False))
        except requests.exceptions.RequestException as request_exception:
            LOGGER.warning("Request exception occurs: {}".format(request_exception))
            raise exceptions.RequestError(request_exception)
        except exceptions.Error:
            raise
        return token
