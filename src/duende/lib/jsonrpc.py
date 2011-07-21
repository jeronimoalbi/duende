# -*- coding: utf8 -*-
#
# Copyright (c) 2011, Jerónimo José Albi <jeronimo.albi@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of copyright holders nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
JSON-RPC module

Specification: http://groups.google.com/group/json-rpc/web/json-rpc-2-0
"""

import simplejson

from datetime import datetime
from datetime import date
from datetime import time

from duende import Response

# JSON-RPC error codes:
# New errors can go from -32099 to -32000
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def get_response(obj, version='2.0'):
    """Create a JSON-RPC Response for given object

    Response will use JSON-RPC version 2.0 by default.

    """

    contents = {}
    if hasattr(object, 'get_dict'):
        contents.update(obj.get_dict())

    contents['jsonrpc'] = version
    contents['id'] = None
    if isinstance(obj, JSONRPCError):
        contents['error'] = obj.get_dict()
    else:
        contents['result'] = obj

    response = JSONResponse()
    response.body = contents

    return response


def simplejson_default(obj):
    """Convert special python classes to JSON compatible values"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()

    error_message = u'%s is not JSON serializable' % repr(obj)

    raise TypeError(error_message)


def simplejson_dumps(value, compact_mode=False):
    """Wapper of simplejson.dumps that allow serialization of complex types"""

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    dump_kwargs = {}
    dump_kwargs['use_decimal'] = True
    dump_kwargs['default'] = simplejson_default

    if compact_mode or not asbool(CONFIG['debug']):
        #when debug=false use compact JSON mode
        dump_kwargs['separators'] = (',', ':')

    return simplejson.dumps(value, **dump_kwargs)


class JSONResponse(Response):
    """Response class for JSON contents

    This class will convert its body contents to a json string.

    """

    default_content_type = 'application/json'
    default_charset = 'utf-8'
    compact_mode = False

    def _body__set(self, value):
        self._body = simplejson_dumps(value, compact_mode=self.compact_mode)
        self.content_length = len(self._body)
        self._app_iter = None

    def _body__get(self):
        if self._body is not None:
            return simplejson.loads(self._body)

    def _body__del(self):
        super(JSONResponse, self)._body__del()

    def get_raw_body(self):
        return self._body

    body = property(_body__get, _body__set, _body__del, doc=_body__get.__doc__)


class JSONRPCError(Exception):
    """Base class for JSON-RPC errors"""

    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data

    def get_dict(self):
        """Get dictionary representation of the error"""

        value = {}
        value['code'] = self.code
        value['message'] = self.message
        value['data'] = self.data

        return value


class JSONRPCCustomError(JSONRPCError):
    """Base class to define custom JSON-RPC errors"""

    code = None
    message = None

    def __init__(self, data=None):
        if not self.code:
            raise Exception(u'Error code not defined')

        if not self.message:
            raise Exception(u'Error message not defined')

        super(JSONRPCCustomError, self).__init__(self.code, self.message,
                                                 data=data)


class JSONPRPCParseError(JSONRPCCustomError):
    code = PARSE_ERROR
    message = u'Parse error'


class JSONRPCInvalidRequest(JSONRPCCustomError):
    code = INVALID_REQUEST
    message = u'Invalid request'


class JSONRPCMethodNotFound(JSONRPCCustomError):
    code = METHOD_NOT_FOUND
    message = u'Method not found'


class JSONRPCInvalidParams(JSONRPCCustomError):
    code = INVALID_PARAMS
    message = u'Invalid params'


class JSONRPCInternalError(JSONRPCCustomError):
    code = INTERNAL_ERROR
    message = u'Internal error'
