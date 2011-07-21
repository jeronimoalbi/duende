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
import gettext as _gettext

from functools import partial

from duende import REQUEST
from duende import get_enabled_app_list
from duende import get_resource_dir


class TranslationManagerError(Exception):
    pass


class TranslationManager(object):
    """Manager for application translations using domains"""

    def __init__(self, locale_list):
        self.locale_list = locale_list
        #TODO: Check if there is no need to add languages
        self.languages = self._parse_languages_in_locale_list()
        self._init_application_domains()

    def _parse_languages_in_locale_list(self):
        """Create a list of locales and languages for missing locale languages

        Locale list can have posix locale and language codes, but it might
        happen that some posix locales in list dont have the language code
        included in same list. So we add there missing language codes to allow
        gettext to use alternative language in case a language for a posix
        locale is not available.

        """

        languages = []
        for locale_code in self.locale_list:
            is_posix_locale = ('_' in locale_code)
            #check to avoid duplicating language codes
            if is_posix_locale or (locale_code not in languages):
                languages.append(locale_code)

            #for posix locales extract locale language
            if is_posix_locale:
                lang_code = locale_code.split('_')[0]
                if lang_code not in languages:
                    languages.append(lang_code)

        return languages

    def _init_application_domains(self):
        self.domains = {}
        for app_name in get_enabled_app_list():
            resource_dir = get_resource_dir(app_name)
            if not resource_dir:
                continue

            locale_dir = os.sep.join([resource_dir, 'locale'])
            if not os.path.isdir(locale_dir):
                continue

            #map a domain to a locale directory.
            #template location will be resolvedi using something
            #like "app_name/path_to/template.xxx" for renderers
            self.domains[app_name] = {
                'locale_dir': locale_dir,
                'translation': None,
            }

    def get_translation(self, domain):
        domain_info = self.domains.get(domain, None)
        if not domain_info:
            msg = u'Invalid translation domain %s' % domain

            raise TranslationManagerError(msg)

        #create translation when is missing
        if not domain_info['translation']:
            locale_dir = domain_info['locale_dir']
            langs = self.languages
            trans = _gettext.translation(domain, locale_dir, languages=langs)
            domain_info['translation'] = trans

        return domain_info['translation']

    def gettext(self, domain, message):
        translation = self.get_translation(domain)

        return translation.ugettext(message)

    def ngettext(self, domain, message, plural_message, count):
        translation = self.get_translation(domain)

        return translation.ungettext(message, plural_message, count)


def get_current_translation_manager():
    """Get TranslationManager for current request"""

    return REQUEST.environ['duende.translation']


def dgettext(domain, message):
    """Translate a message using current request translation manager"""

    translation_mgr = get_current_translation_manager()

    return translation_mgr.gettext(domain, message)


def dngettext(domain, message, plural_message, count):
    """Translate a plural message using current request translation manager"""

    translation_mgr = get_current_translation_manager()

    return translation_mgr.ngettext(domain, message, plural_message, count)


def get_translation_fn(name):
    """Get a translation function for a given domain.

    A partial dgettext function will be returned with domain
    as fixed parameter of partial function.

    """

    fn = partial(dgettext, name)
    fn.__name__ = 'partial_dgettext'
    fn.__doc__ = 'Partial gettext function for domain %s' % name

    return fn


def get_plural_translation_fn(name):
    """Get a plural form translation function for a given domain.

    A partial dngettext function will be returned with domain
    as fixed parameter of partial function.

    """

    fn = partial(dngettext, name)
    fn.__name__ = 'partial_dngettext'
    fn.__doc__ = 'Partial ngettext function for domain %s' % name

    return fn
