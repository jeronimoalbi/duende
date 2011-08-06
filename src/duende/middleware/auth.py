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

from paste.deploy.converters import asbool

from duende import SESSION
from duende import httpexc
from duende.lib import urls
from duende.lib import jsonrpc
from duende.middleware import MiddlewareException

LOG = logging.getLogger(__name__)


class AuthMiddleware:
    """Middleware to enable form autentication."""

    def __init__(self, application, config):
        self.application = application
        self.config = config
        self.debug = asbool(config['debug'])
        self.default_public = asbool(config['auth.default_public'])
        self.login_url = urls.url(config.get('auth.login'))

    def _handle_unauthorized(self, environ):
        LOG.info(u'Unauthorized request from %s', environ['REMOTE_ADDR'])

        is_xmlhttp_request = jsonrpc.is_xmlhttp_request(environ)
        #TODO: Add basic auth for JSON requests
        if is_xmlhttp_request and jsonrpc.request_accept_json(environ):
            compact_json = not self.debug

            raise jsonrpc.JSONRPCUnauthorized(compact=compact_json)
        elif login_url:
            LOG.debug(u'Redirecting to login page %s', self.login_url)
            #redirect non JSON requests to login page
            raise httpexc.HTTPFound(location=self.login_url)

        #when no login page is available and JSON request dont
        #accept JSON response raise HTTP unauthorized
        raise httpexc.HTTPUnauthorized()

    def __call__(self, environ, start_response):
        view_handler = environ.get('duende.view')
        is_public_view = getattr(view_handler, 'public', self.default_public)
        session = environ['beaker.session']
        user = session.get('user', None)
        if not (is_public_view or user):
            self._handle_unauthorized(environ)

        environ['SESSION_ID'] = session.id
        if user:
            environ['REMOTE_USER'] = user.get_username()

        return self.application(environ, start_response)
