"""
client for proxyvor
"""
from __future__ import unicode_literals
import proxyvor.tools.exceptions as exceptions
import traceback
from proxyvor import client as proxyvor_client
import logging
import logging.config


if __name__ == '__main__':
    LOGGER = None
    try:
        PROG_ARGS = proxyvor_client.parse_args()
        CONFIG = proxyvor_client.parse_config_file(PROG_ARGS.get('config_file_path', ""))
        LOGGER_CONFIG = CONFIG.get('logger')
        if not LOGGER_CONFIG:
            print "You must specify a 'logger' key in the config file"
            exit(1)
        logging.config.dictConfig(LOGGER_CONFIG)
        LOGGER = logging.getLogger()
        REFLECTOR = proxyvor_client.build_reflector_handler(CONFIG.get('target', {}))
        LOGGER.info("Testing {0}://{1}:{2} with reflector: {3}".format(PROG_ARGS.get('proxy_type'),
                                                                       PROG_ARGS.get('proxy_ip'),
                                                                       PROG_ARGS.get('proxy_port'),
                                                                       REFLECTOR.target_data().get('base_url')))
        PROXY_DATA = {'ip': PROG_ARGS.get('proxy_ip', "127.0.0.1"),
                      'port': PROG_ARGS.get('proxy_port', 80),
                      'type': PROG_ARGS.get('proxy_type', 'http')}
        PLUGINS = proxyvor_client.load_plugins(CONFIG.get("plugin_path", ''), CONFIG, PROXY_DATA)
        RESULT = proxyvor_client.run(PROXY_DATA['ip'],
                                     PROXY_DATA['port'],
                                     PROXY_DATA['type'],
                                     REFLECTOR)
        LOGGER.debug(RESULT)
        proxyvor_client.run_plugin(PLUGINS, 'ProxyAnalyzer', RESULT)
        proxyvor_client.run_plugin(PLUGINS, 'geoip2', RESULT)

    except exceptions.Error as p_exc:
        if LOGGER:
            LOGGER.warning("Proxyvor Exceptions occurs: {0}, {1}".format(type(p_exc), p_exc))
            LOGGER.debug("**********INFORMATIONS**********")
            LOGGER.exception("Traceback: ")
            LOGGER.debug("********************************")
        else:
            print "Proxyvor Exceptions occurs: ", type(p_exc), p_exc
            print "**********INFORMATIONS**********"
            traceback.print_exc()
            print "********************************"

    except Exception as exc:
        if LOGGER:
            LOGGER.warning("Exceptions occurs: {0}, {1}".format(type(p_exc), p_exc))
            LOGGER.debug("**********INFORMATIONS**********")
            LOGGER.exception("Traceback: ")
            LOGGER.debug("********************************")
        else:
            print "Proxyvor Exceptions occurs: ", type(exc), exc
            print "**********INFORMATIONS**********"
            traceback.print_exc()
            print "********************************"
