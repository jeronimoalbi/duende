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
import mimetypes

from paste import fileapp
from paste import urlparser

#types that should be served as UTF8
UTF_TYPES = (
    'text/css',
    'application/x-javascript',
    'application/javascript',
    'text/html',
    'text/xml',
    'application/xml',
    'application/xhtml+xm',
    'text/plain',
    'text/csv',
)


class StaticContentMiddleware(urlparser.StaticURLParser):
    """Static contents serving middleware"""

    def make_app(self, file_name):
        (content_type, encoding) = mimetypes.guess_type(file_name)

        #set utf8 for known types
        if content_type in UTF_TYPES:
            content_type = content_type + '; charset=utf8'

        headers = [
            ('Content-Type', content_type)
        ]
        application = fileapp.FileApp(file_name, content_type=content_type)

        return application
