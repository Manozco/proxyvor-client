from __future__ import unicode_literals
import proxyvor.tools.json_wrapper as json
import argparse
import re
from proxyvor import reflector_handler
from proxyvor import tester
import proxyvor.plugin as plugin
import sys
import logging

PROXY_TESTERS = {'http': tester.HttpTester,
                 'socks5': tester.Socks5Tester,
                 'socks4': tester.Socks4Tester}
LOGGER = logging.getLogger()


def parse_args():
    """"parse arguments"""
    ret = {}
    parser = argparse.ArgumentParser(description='test proxys')
    parser.add_argument('-i',
                        '--ip',
                        default='127.0.0.1',
                        help='specify ip to test, default 127.0.0.1')
    parser.add_argument('-p',
                        '--port',
                        default=80,
                        help='specify port to test, default 80')
    parser.add_argument('-t',
                        '--type',
                        default='http',
                        help='specify protocol to test, default to http')
    parser.add_argument('-c',
                        '--config',
                        default='config.json',
                        help='specify config file, default is config.json')
    args = parser.parse_args()

    if args.ip:
        if not re.match(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', args.ip):
            ret['proxy_ip'] = '127.0.0.1'
        else:
            ret['proxy_ip'] = args.ip

    if args.port:
        ret['proxy_port'] = 80
        try:
            ret['proxy_port'] = int(args.port)
        except ValueError:
            print "CRITICAL: The port specified ({0}) can not be converted to int".format(args.port)
            sys.exit(2)
        if not ret['proxy_port'] in range(1, 65535):
            ret['proxy_port'] = 80

    if args.type:
        if args.type not in PROXY_TESTERS.keys():
            print 'For the moment, only those proxys are supported: ', PROXY_TESTERS.keys()
            ret['proxy_type'] = 'http'
        else:
            ret['proxy_type'] = args.type

    if args.config:
        ret['config_file_path'] = 'config.json'
        try:
            with open(args.config, 'r'):
                ret['config_file_path'] = args.config
        except IOError:
            print "CRITICAL: The config file specified ({0}) can not be converted to int".format(args.config)
            sys.exit(2)
    return ret


def parse_config_file(config_file_path):
    """"parse config file"""
    config_file = None
    ret = {}
    try:
        config_file = open(config_file_path)

    except IOError:
        print "Cannot parse config_file: {}".format(config_file_path)
        sys.exit(1)

    ret = json.load(config_file)
    if config_file:
        config_file.close()
    return ret


def build_reflector_handler(reflector_data):
    """build the reflector_handler"""
    return reflector_handler.ReflectorHandler(reflector_data)


def load_plugins(path, config_data=None, proxy_data=None):
    """load all the plugins"""
    if not config_data:
        config_data = {}
    if not proxy_data:
        proxy_data = {}
    return plugin.load(path, {'config': config_data, 'proxy': proxy_data})


def run_plugin(plugins_dict, name, result=None):
    """run specific plugin according to the folder name OR the name specified in
    the plugin_config.json file
    """
    plugins_names = {}
    for plugin_obj in plugins_dict.values():
        plugins_names[plugin_obj.name()] = plugin_obj

    if name in plugins_dict:
        plugins_dict[name].run(result)
    elif name in plugins_names:
        plugins_names[name].run(result)
    else:
        LOGGER.warning("No plugin with name: {0} found".format(name))


def run(proxy_ip, proxy_port, proxy_type, reflector):
    """run test; return result"""
    proxy_tester = PROXY_TESTERS.get(proxy_type)(proxy_ip, proxy_port, reflector)
    proxy_tester.test()
    return proxy_tester.result()
