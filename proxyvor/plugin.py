"""
module for handlling plugins
A plugin is a directory containing:
- main.py
- plugin_config.json


main.py MUST contain a Plugin class which will be instantiated
The Plugin class MUST inherit the class Plugin defined in this file
The Plugin class MUST have the same parameters than the base one
It also must have a run method with the same parameters as the base one

the plugin_config.json must be of the form:
{
    'author': "author_name",
    'name': "plugin_name",
    'version': "plugin_version",
    'description': "plugin_description",
    'extra': {}
}
The 'extra' object will be stored in self._plugin_config
"""

import proxyvor.tester_result as tester_result
import sys
import os
import proxyvor.tools.json_wrapper as json
import imp
import proxyvor.tools.exceptions as exceptions
import logging

LOGGER = logging.getLogger()


class ProxyvorClientBasePlugin(object):
    """
    base class for proxyvor plugins
    must be inherited
    """
    #pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, plugin_config_path, data=None):
        if data:
            assert isinstance(data, dict)
        else:
            data = {}
        self._config = data.get('config')
        if not self._config:
            raise exceptions.BadConfigurationError("ProxyvorClientBasePlugin expects data to contains key 'config'")
        self._proxy_data = data.get('proxy')
        if not self._config:
            raise exceptions.BadConfigurationError("ProxyvorClientBasePlugin expects data to contains key 'proxy'")
        self.logger = LOGGER

        self._author = None
        self._name = None
        self._version = None
        self._description = None
        self._extra = None
        self._config_file_path = None

        try:
            config = json.load(open(plugin_config_path, 'r'))
            self._author = config.get('author', "")
            self._name = config.get('name', "")
            self._version = config.get('version', "")
            self._description = config.get('description', "")
            self._plugin_config = config.get('extra', {})
            self._config_file_path = plugin_config_path

        except exceptions.JsonLoadError:
            "Error while parsing config_file: {}".format(plugin_config_path)
            raise

    def run(self, result=None):
        """
        Method to implement
        """
        #pylint: disable=no-self-use
        if result:
            assert isinstance(result, tester_result.ProxyResult)
        raise exceptions.NotImplementedError("You have to implement this method 'run'")

    def name(self):
        #pylint: disable=missing-docstring
        return self._name

    def __str__(self):
        ret = ""
        ret += 'Name: ' + self._name + "\n"
        ret += 'Author: ' + self._author + "\n"
        ret += 'Version: ' + self._version + "\n"
        ret += 'Description: ' + self._description + "\n"
        return ret

    def log(self, msg="", level=0):
        """
        will log the msg prefixed by the plugin name
        level is:
        0: debug
        1: info
        2; warning
        3: error
        4: critical
        else: debug
        """
        message = "{0} - {1}".format(self._name, msg)
        if level == 0:
            self.logger.debug(message)
        elif level == 1:
            self.logger.info(message)
        elif level == 2:
            self.logger.warning(message)
        elif level == 3:
            self.logger.error(message)
        elif level == 4:
            self.logger.critical(message)
        else:
            self.logger.debug(message)


def load(path_plugins, data):
    """load all the plugins in the path"""
    def get_full_path_file(shortname):
        #pylint: disable=missing-docstring
        return os.path.join(path_plugins, shortname)
    plugins = {}
    full_path_files = [get_full_path_file(shortname) for shortname in os.listdir(path_plugins)]
    folders = [folder for folder in full_path_files if os.path.isdir(folder)]
    for folder in folders:
        plugin_files = os.listdir(folder)
        if "main.py" in plugin_files and "plugin_config.json" in plugin_files:
            sys.path.insert(0, folder)
            found_module = imp.find_module('main')
            if found_module:
                mod = imp.load_module('{0}_plugin'.format(folder), found_module[0], found_module[1], found_module[2])
            else:
                raise exceptions.ImportError("Module not found: {0}".format(folder))
            try:
                plugins[os.path.basename(folder)] = mod.Plugin(os.path.abspath(os.path.join(folder, "plugin_config.json")),
                                                               data)
            except AttributeError:
                raise exceptions.AttributeError("No attribute Plugin in {0}, {1}".format(mod, found_module))
            sys.path.pop(0)
        elif "main.py" in plugin_files and not "plugin_config.json" in plugin_files:
            LOGGER.warning("Cannot load the plugin {} because there is no plugin_config.json".format(folder))
    return plugins


def print_all_plugins(plugins_dict):
    #pylint: disable=missing-docstring
    assert isinstance(plugins_dict, dict)
    for name, plugin in plugins_dict.items():
        LOGGER.debug("*********" + name + "*********")
        LOGGER.debug(plugin)
        LOGGER.debug("\n")
