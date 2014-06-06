# """plugin for doing geoip2 lookups on proxys"""

import proxyvor.plugin as plugin
class Plugin(plugin.ProxyvorClientBasePlugin):
    """
    fake plugin for keeping the code of geoip2 plugin but disabling it
    """
    def __init__(self, plugin_config_path, data):
        super(Plugin, self).__init__(plugin_config_path, data)
    def run(self, result):
        pass

# import re
# import geoip2.webservice
# from geoip2.errors import GeoIP2Error
# import proxyvor.tools.json_wrapper as json
# import proxyvor.tools.exceptions as exceptions


# def get_ips(haystack):
#     """return all the ip addresses in haystack"""
#     return set(re.findall(r'((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))',
#                           haystack))


# class Plugin(plugin.ProxyvorClientBasePlugin):
#     #pylint: disable=missing-docstring
#     def __init__(self, plugin_config_path, data):
#         super(Plugin, self).__init__(plugin_config_path, data)
#         self._credential_user, self._credential_key = self.get_geoip2_credentials()

#     def run(self, result):
#         proxy_part = result.proxy()
#         result = {}
#         ips_to_test = [proxy_part.get("client_ip", ""),
#                        proxy_part.get("remote_addr", ""),
#                        str(self._proxy_data.get("ip", ""))]
#         ips_to_test.extend(proxy_part.get("client_remote_route", []))
#         for ip in ips_to_test:
#             if not result.get(ip):
#                 result[ip] = self.geoip_informations(ip)
#         self.log(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')), 1)

#     def get_geoip2_credentials(self):
#         credentials = self._plugin_config.get('credentials', {})
#         return credentials.get('user', 0), credentials.get('key', "")

#     def geoip_informations(self, ip_addr):
#         geoipClient = geoip2.webservice.Client(self._credential_user, self._credential_key)
#         try:
#             response = geoipClient.omni(ip_addr)
#             responseObject = {
#                 "host": ip_addr,
#                 "ip_str": ip_addr,
#                 "location": {
#                     "country_name": response.country.name,
#                     "country_code": response.country.iso_code,
#                     "latitude": response.location.latitude,
#                     "longitude": response.location.longitude
#                 },
#                 "city": {
#                     "confidence": response.city.confidence,
#                     "names": response.city.names
#                 },
#                 "as_number": response.traits.autonomous_system_number,
#                 "as_organization": response.traits.autonomous_system_organization,
#                 "isp": response.traits.isp,
#                 "domains": [response.traits.domain],
#                 "org": response.traits.organization,
#                 "is_proxy": response.traits.is_anonymous_proxy,
#                 "user_type": response.traits.user_type
#             }
#             return responseObject
#         except GeoIP2Error as e:
#             self.log('Error: {0}'.format(e), 3)
#             raise exceptions.GeoIP2Error(e)
#         except ValueError as e:
#             self.log('Error: {0}'.format(e), 3)
#             raise exceptions.PluginError(e)
