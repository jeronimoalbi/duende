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

import babel
import formencode

from duende.lib.i18n import translation
from duende.lib.i18n import get_http_locales

LOG = logging.getLogger(__name__)


class LocaleMiddleware:
    """Middleware to initialize locale and gettext translation support."""

    def __init__(self, application, config):
        self.application = application
        self.config = config

    def init_request_translation(self, environ):
        #TODO: Allow setting locale using request parameters
        accept_language = environ['HTTP_ACCEPT_LANGUAGE']
        default_locale = self.config['default_locale']
        #initialize a locale instance for current request
        locale_list = get_http_locales(accept_language, default=default_locale)

        #create an save translation manager inside request environment
        translation_mgr = translation.TranslationManager(locale_list)
        environ['duende.translation'] = translation_mgr

    def init_request_locale(self, environ):
        translation = environ['duende.translation']
        for code in translation.locale_list:
            try:
                environ['duende.locale'] = babel.Locale.parse(code)
                LOG.debug(u'Using locale %s', code)
                #after sucessfully setting a locale skip other locales
                break
            except babel.UnknownLocaleError:
                #skip unknown locales
                pass

    def init_formencode_language(self, environ):
        language = environ['duende.locale'].language
        #TODO: Use all request languages instead of only current one
        formencode.api.set_stdtranslation(languages=[language])

    def __call__(self, environ, start_response):
        self.init_request_translation(environ)
        self.init_request_locale(environ)
        self.init_formencode_language(environ)

        return self.application(environ, start_response)
