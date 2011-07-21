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

#Locale reference: http://babel.edgewall.org/wiki/Documentation/display.html
from babel import Locale


def locale_to_posix(locale):
    """Convert a locale code to posix"""

    if '-' not in locale:
        return locale

    (lang_code, country_code) = locale.split('-')
    locale = '%s_%s' % (lang_code, country_code.upper())

    return locale


def get_http_locales(accept_language, default='en_US'):
    """Determines locale from an HTTP Accept-Language header

    Return a list of posix locale codes and language codes.
    Parameter accept_language is a string with contents of request
    HTTP_ACCEPT_LANGUAGE.

    See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4

    """

    default = locale_to_posix(default)

    if accept_language:
        locales = []

        for language in accept_language.split(','):
            parts = language.strip()
            #split language from score
            parts = parts.split(';')

            #get language score
            if len(parts) > 1 and parts[1].startswith('q='):
                try:
                    score = float(parts[1][2:])
                except (ValueError, TypeError):
                    score = 0.0
            else:
                score = 1.0

            locale_code = locale_to_posix(parts[0])
            locales.append((locale_code, score))

        if locales:
            #sort locales by score
            locales.sort(key=lambda pair: pair[1], reverse=True)
            #egnerate and return list of posix locale codes
            locale_codes = [locale_code for (locale_code, score) in locales]
            if default not in locale_codes:
                locale_codes.append(default)

            return locale_codes

    return [default]
