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

import simplejson

from functools import wraps

from duende import Response
from duende import httpexc
from duende.lib import jsonrpc
from duende.lib.jsonrpc import JSONResponse


def restrict(method):
    """Decorator to restrict request method to a view"""

    def _restrict(func):

        @wraps(func)
        def _restrict_wrap(request, *args, **kwargs):
            if request.method == method:
                response = func(request, *args, **kwargs)
            else:
                err = httpexc.HTTPMethodNotAllowed()
                response = request.get_response(err)

            return response

        return _restrict_wrap

    return _restrict


def redirect(func):
    """Decorator to perform an URL redirection after view finishes

    Handler must return a string with a URL to redirect to.

    """

    @wraps(func)
    def _redirect_wrap(*args, **kwargs):
        url = func(*args, **kwargs)
        if not isinstance(url, basestring) or not url:
            msg = u'View %s must return a valid URL' % func

            raise Exception(msg)

        raise httpexc.HTTPFound(location=url)

    return _redirect_wrap


def text(encoding='utf8'):
    """Decorator for request of type text/plain in a given encoding

    View handler must return a unicode string.
    If None is returned then empty string will be assigned to response body.
    By default response body is encoded in UTF-8

    """

    def _text(func):

        @wraps(func)
        def _text_wrap(*args, **kwargs):
            contents = func(*args, **kwargs)
            if not contents:
                contents = u''
            elif not isinstance(contents, unicode):
                view_handler_name = func.__name__
                msg = u'Non unicode returned from view handler %s' \
                    % view_handler_name

                raise Exception(msg)

            #create response for current template
            response = Response()
            response.headers['Content-Type'] = 'text/plain'
            response.charset = encoding
            response.unicode_body = contents

            return response

        return _text_wrap

    return _text


def utf8_text(func):
    """Decorator for request of type text/plain in UTF-8

    View handler must return a unicode string or an utf8 string.
    If None is returned then empty string will be assigned to response body.

    """

    @wraps(func)
    def _utf8_text_wrap(*args, **kwargs):
        contents = func(*args, **kwargs)
        if isinstance(contents, unicode):
            contents = contents.encode('utf8')
        elif not isinstance(contents, basestring):
            contents = ''

        #create response for current template
        response = Response()
        response.headers['Content-Type'] = 'text/plain'
        response.body = contents

        return response

    return _utf8_text_wrap


def json(func):
    """Decorator for request of type application/json."""

    @wraps(func)
    def _json_wrap(*args, **kwargs):
        contents = func(*args, **kwargs)
        response = JSONResponse()
        response.body = contents

        return response

    return _json_wrap


def json_rpc(func):
    """Decorator for JSON-RPC requests of type application/json

    View handler can return instances of araneus.router.lib.jsonrpc.JSONError
    to comunicate server errors.

    """

    @wraps(func)
    def _json_rpc_wrap(*args, **kwargs):
        contents = func(*args, **kwargs)
        response = jsonrpc.get_response(contents)

        return response

    return _json_rpc_wrap


def xml(func):
    """Decorator for request of type text/xml

    View has to return the XML string or a tuple with file name as
    first value and XML string as second.

    """

    @wraps(func)
    def _xml_wrap(*args, **kwargs):
        contents = func(*args, **kwargs)
        file_name = None
        if isinstance(contents, tuple):
            file_name = contents[0]
            contents = contents[1]

        response = Response()
        if isinstance(contents, unicode):
            contents = contents.encode('utf8')
            response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        else:
            response.headers['Content-Type'] = 'text/xml'

        response.body = contents

        if file_name:
            content_disposition = u'attachment; filename=%s' % file_name
            response.headers['Content-Disposition'] = content_disposition

        return response

    return _xml_wrap
