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

from babel.dates import format_date as _format_date
from babel.dates import format_datetime as _format_datetime
from babel.dates import format_time as _format_time

from duende import REQUEST

SHORT = 'short'
MEDIUM = 'madium'
LONG = 'long'
FULL = 'full'


def get_current_locale_code():
    """Get locale code for current request"""

    locale = REQUEST['duende.locale']

    if not locale.territory:
        return locale.language

    return '%s_%s' % (locale.language, locale.territory)


def format_date(date, format=MEDIUM):
    """Format date using current locale"""

    if not date:
        return date

    locale = get_current_locale_code()

    return _format_date(date, format=format, locale=locale)


def format_time(time, format=MEDIUM):
    """Format time using current locale"""

    if not time:
        return time

    locale = get_current_locale_code()

    return _format_time(time, format=format, locale=locale)


def format_datetime(datetime, format=MEDIUM):
    """Format datetime using current locale"""

    if not datetime:
        return datetime

    locale = get_current_locale_code()

    return _format_datetime(datetime, format=format, locale=locale)
