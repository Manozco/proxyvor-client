"""plugin for analyzing proxys"""
import proxyvor.plugin as plugin


BAD_ANONYMITY = -1
NEUTRAL = 0
GOOD_ANONYMITY = 1
BAD_HEADERS_FOR_PROXY = ["Via",
                         "X-Proxy-Id", ]


class Plugin(plugin.ProxyvorClientBasePlugin):
    #pylint: disable=missing-docstring
    def __init__(self, plugin_config_path, data):
        super(Plugin, self).__init__(plugin_config_path, data)
        self._result = None
        self._proxy = None
        self._real = None

    def run(self, result=None):
        self._result = result
        self._proxy = result.proxy()
        self._real = result.real()
        if not self._real:
            self.log("missing the real part, comparison will not be exploitable", 2)
        if not self._proxy:
            self.log("missing the proxy part, comparison will not be exploitable", 2)

        anonymity = self.compare_anonymity()
        if anonymity == BAD_ANONYMITY:
            self.log("Bad anonymity (your ip address is visible)", 1)
        elif anonymity == NEUTRAL:
            self.log("""Neutral anonymity (your ip address is not here but the server knows you are using a proxy)""", 1)
        elif anonymity == GOOD_ANONYMITY:
            self.log("You are anonymous", 1)

        quality = self.compare_quality()
        if quality is False:
            self.log("Bad quality, The proxy may changes your headers", 1)
        else:
            self.log("Good quality, nothing bad detected", 1)

    def compare_anonymity(self):
        """
        If proxy_result contains real_ip, proxy is bad for anonimity
        else if proxy_result contains just a via header, proxy is neutral for anonimity
        else proxy is good for anonimity
        self._BAD_ANONYMITY: result is not good for anonimity
        self._NEUTRAL: result is neutral (or not exploitable)
        self._GOOD_ANONYMITY: result is good for anonymity
        """
        if (self._result.real_client_ip() in self._proxy.get('client_ip', '')
            or self._result.real_client_ip() in self._proxy.get('client_remote_route', [])
            or self._result.real_client_ip() in self._proxy.get('remote_addr', '')):
            return BAD_ANONYMITY
        for key in self._proxy.get('http_headers', {}):
            if key == "Host":
                continue
            if (self._result.real_client_ip() in key or
                self._result.real_client_ip() in self._proxy.get('http_headers', {}).get(key)):
                return BAD_ANONYMITY

        for bad_header in BAD_HEADERS_FOR_PROXY:
            if bad_header in list(self._proxy.get('http_headers', {}).keys()):
                return NEUTRAL

        return GOOD_ANONYMITY

    def compare_quality(self):
        """
        if proxy blocks some of our headers, we might have problem in the future
        so we return bad quality
        this result is independent of the anonymity comaparison
        """
        proxy_ip = self._proxy_data.get('ip', '')
        if (proxy_ip and self._proxy and
            (not proxy_ip in self._proxy.get('client_ip', '') and
             not proxy_ip in self._proxy.get('client_remote_route', []) and
             not proxy_ip in self._proxy.get('remote_addr', ''))):
            self.logger.info("Warning: The proxy ip is not in the result, the proxy may be proxified")

        if not self._proxy.get('http_headers', {}).get('User-Agent'):
            return False
        if (self._proxy.get('http_headers', {}).get('User-Agent') !=
            self._real.get('http_headers', {}).get('User-Agent')):
            return False

        return True
