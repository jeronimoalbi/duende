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

from duende import Request
from duende import httpexc


class LimitUploadSizeMiddleware:
    """Limit file uploads requests greater than a size.

    Full reponse size is actually evaluated.
    When using an asynchronous web server like nginx/lighttpd
    request is sent in one go to WSGI app, so size limit must
    be done by web server.

    """

    def __init__(self, app, max_size):
        self.app = app
        self.max_size = max_size

    def __call__(self, environ, start_response):
        response = None
        request = Request(environ)

        if request.method == 'POST':
            size = request.headers.get('Content-length')
            if not size:
                msg = u'No content-length header specified'
                response = httpexc.HTTPBadRequest(msg)
            elif int(size) > self.max_size:
                msg = u'POST body exceeds maximum limits'
                response = httpexc.HTTPBadRequest(msg)

        if not response:
            response = request.get_response(self.app)

        return response(environ, start_response)
