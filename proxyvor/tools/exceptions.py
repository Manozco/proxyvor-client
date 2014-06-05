"""
module for defining our own Errors
"""
#pylint: disable=redefined-builtin


class Error(Exception):
    """base class for Errors in proxyvor"""
    pass


class JsonError(Error):
    """base class for json related Errors"""
    pass


class JsonLoadError(JsonError):
    #pylint: disable=missing-docstring
    pass


class JsonDumpError(JsonError):
    #pylint: disable=missing-docstring
    pass


class BadConfigurationError(Error):
    #pylint: disable=missing-docstring
    pass


class NotImplementedError(Error):
    #pylint: disable=missing-docstring
    pass


class ImportError(Error):
    #pylint: disable=missing-docstring
    pass


class AttributeError(Error):
    #pylint: disable=missing-docstring
    pass


class LibError(Error):
    #pylint: disable=missing-docstring
    pass


class NetworkLibError(LibError):
    #pylint: disable=missing-docstring
    pass


class RequestError(NetworkLibError):
    #pylint: disable=missing-docstring
    pass


class UrllibError(NetworkLibError):
    #pylint: disable=missing-docstring
    pass


class PyCurlError(NetworkLibError):
    #pylint: disable=missing-docstring
    pass


class ProxyvorGeoIP2Error(LibError):
    #pylint: disable=missing-docstring
    pass


class PluginError(Error):
    #pylint: disable=missing-docstring
    pass
