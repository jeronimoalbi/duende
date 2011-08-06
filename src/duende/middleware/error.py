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

import logging

from wsgiref.util import request_uri
from paste.deploy.converters import asbool

from duende import httpexc
from duende.lib import jsonrpc

LOG = logging.getLogger(__name__)


class ErrorMiddleware:
    """Middleware in charge of handling application errors"""

    def __init__(self, application, config):
        self.application = application
        self.config = config
        self.debug = asbool(self.config['debug'])
        self.debug_requests = asbool(self.config.get('debug.requests'))

    def __call__(self, environ, start_response):
        try:
            response = self.application(environ, start_response)
        except (httpexc.HTTPException, jsonrpc.JSONRPCCustomError), exc:
            #on HTTP errors create a proper response for it
            response = exc(environ, start_response)
        except Exception:
            LOG.exception(u'Unable to get response')
            #when debugging raise error
            if self.debug:
                raise

            #when JSON is used return JSON-RPC result
            http_requested_with = environ.get('HTTP_X_REQUESTED_WITH')
            is_xmlhttp = (http_requested_with == 'XMLHttpRequest')
            if is_xmlhttp and ('application/json' in environ['HTTP_ACCEPT']):
                compact_json = not self.debug
                err = jsonrpc.JSONRPCInternalError(compact=compact_json)
            else:
                #TODO: Display nice internal server error page
                err = httpexc.HTTPInternalServerError()

            response = err(environ, start_response)

        if self.debug and self.debug_requests:
            #try to get response status code.
            #for resources response might not be a Response instance
            status = getattr(response, 'status', '200 OK')
            #log request status and URL
            uri = request_uri(environ, include_query=0)
            LOG.debug(u'[%s] %s', status, uri)

        return response
