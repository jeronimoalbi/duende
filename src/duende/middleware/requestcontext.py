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

from duende import SESSION
from duende import REQUEST
from duende import Request
from duende.middleware import MiddlewareException


class RequestContextMiddleware(object):
    """Middleware that register context for current request

    Register global application variables like SESSION and REQUEST.

    """

    def __init__(self, application):
        self.application = application

    @staticmethod
    def init_request_global(environ):
        global REQUEST

        request = Request(environ)
        environ['paste.registry'].register(REQUEST, request)

    @staticmethod
    def init_session_global(environ):
        global SESSION

        session_manager = environ['beaker.session']
        environ['paste.registry'].register(SESSION, session_manager)

    def __call__(self, environ, start_response):
        if 'paste.registry' not in environ:
            raise MiddlewareException(u'Paste RegistryManager is not enabled')

        if 'beaker.session' not in environ:
            msg = u'Beaker SessionMiddleware is not enabled'

            raise MiddlewareException(msg)

        self.init_session_global(environ)
        self.init_request_global(environ)

        return self.application(environ, start_response)
