"""
module for wrapping (basically) json operations
"""

import json
import proxyvor.tools.exceptions as exceptions


def load(fp, **kargs):
    #pylint: disable=missing-docstring,invalid-name
    ret = {}
    try:
        ret = json.load(fp, **kargs)
    except Exception as dummy:
        raise exceptions.JsonLoadError("Impossible to load {0}".format(fp))
    return ret or {}


def loads(s, **kargs):
    #pylint: disable=missing-docstring,invalid-name
    ret = {}
    if isinstance(s, bytes):
        s = s.decode()
    try:
        ret = json.loads(s, **kargs)
    except Exception:
        raise exceptions.JsonLoadError("Impossible to loads {0}".format(s))
    return ret or {}


def dumps(obj, **kargs):
    #pylint: disable=missing-docstring,invalid-name
    ret = ""
    try:
        ret = json.dumps(obj, **kargs)
    except Exception as dummy:
        raise exceptions.JsonDumpError('Impossible to dump {}'.format(obj))
    return ret
