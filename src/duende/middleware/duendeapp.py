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

from duende import SESSION
from duende import REQUEST
from duende import Request
from duende.lib import db
from duende.lib import template
from duende.lib import urls
from duende.middleware import MiddlewareException
from duende.lib.i18n import translation
from duende.lib.i18n import get_http_locales

LOG = logging.getLogger(__name__)


class DuendeApplicationException(Exception):
    pass


class DuendeApplication(object):
    """Middleware that register application context for current request

    Register global application variables like SESSION and REQUEST,
    database and template engines.

    """

    def __init__(self, config):
        self.config = config
        self.default_locale = self.config['default_locale']

        urls.init_application_urls(self.config['url.file'])
        template.init_template_environment(self.config)
        db.init_database_engine(self.config)
        db.init_database_session()

    def _init_globals(self, environ):
        global REQUEST
        global SESSION

        if 'paste.registry' not in environ:
            raise MiddlewareException(u'Paste RegistryManager is not enabled')

        if 'beaker.session' not in environ:
            msg = u'Beaker SessionMiddleware is not enabled'

            raise MiddlewareException(msg)

        session_manager = environ['beaker.session']
        environ['paste.registry'].register(SESSION, session_manager)

        request = Request(environ)
        environ['paste.registry'].register(REQUEST, request)

    def _init_translations(self, environ):
        #TODO: Allow setting locale using request parameters
        #get locale list from current request
        accept_language = environ['HTTP_ACCEPT_LANGUAGE']
        locale_list = get_http_locales(accept_language,
                                       default=self.default_locale)

        #create an save translation manager for current request languages
        self.translation = translation.TranslationManager(locale_list)
        environ['duende.translation'] = self.translation

        #install template engine translation functions
        gettext = translation.dgettext
        ngettext = translation.dngettext
        TPL_ENV = template.ENVIRON
        TPL_ENV.install_gettext_callables(gettext, ngettext, newstyle=True)

    def _init_locale(self, environ):
        locale = None
        translation = self.translation
        for code in translation.locale_list:
            try:
                locale = babel.Locale.parse(code)
                environ['duende.locale'] = locale
                LOG.debug(u'Using locale %s', code)
                #after sucessfully setting a locale skip other locales
                break
            except babel.UnknownLocaleError:
                #skip unknown locales
                pass

        #TODO: Use all request languages instead of only current one
        language = getattr(locale, 'language', self.default_locale)
        formencode.api.set_stdtranslation(languages=[language])

    def __call__(self, environ, start_response):

        def clear_start_response(status, response_headers, exc_info=None):
            """Sub start_response for cleaning after content generation"""

            try:
                return start_response(status, response_headers, exc_info)
            finally:
                #allways clean session connections
                #TODO: Check if this is not going to mess with other requests
                db.clean_database_session()

        #get view handler from environ
        view_handler = environ.get('duende.view')
        if not view_handler:
            msg = u'No view handler available in environment !'

            raise DuendeApplicationException(msg)

        #init request context
        self._init_translations(environ)
        self._init_locale(environ)
        self._init_globals(environ)

        response = view_handler(REQUEST)

        return response(environ, clear_start_response)
