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

import os

from pkg_resources import require

from webob import Request
from webob import Response
from webob import exc as httpexc
from paste.registry import StackedObjectProxy

from duende.lib import urls
from duende.lib.config import CONFIG


CACHE = StackedObjectProxy(name='cache')
SESSION = StackedObjectProxy(name='session')
REQUEST = StackedObjectProxy(name='request')


def get_enabled_app_list():
    """Get a list with names of all enabled applications."""


    mapping = urls.get_url_mapping()

    return mapping.keys()


def guess_version(app_name, file_name):
    """Get current application version

    Version can be successfuly getted when app is installed, and is being
    imported from the installed directory (not from current location).

    """

    version = '(not installed)'
    try:
        info = require(app_name)[0]
        base_path = os.path.dirname(file_name)
        base_path = os.path.dirname(base_path)
        #for applications with namespace we need to dig one more level
        if '.' in app_name:
            base_path = os.path.dirname(base_path)

        if base_path == info.location:
            version = info.version
    except Exception:
        pass

    return version


__version__ = guess_version('duende', __file__)
