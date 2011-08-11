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

import re
import unicodedata

#slugify regexps
SLUG_INVALID_RE = re.compile(ur'[^\w\s-]')
SLUG_HYPENATE_RE = re.compile(ur'[-\s]+')


class TextEncodingException(Exception):
    def __str__(self):
        return 'Text must be unicode or a UTF8 string'


def utf8_to_unicode(text):
    """Convert an UTF8 string to unicode"""

    if not isinstance(text, unicode):
        try:
            text = unicode(text, 'utf8')
        except UnicodeDecodeError:
            raise TextEncodingException()

    return text


def slugify(text):
    """Convert any string to a safe ASCII string

    Convert letters to lowercase, replace spaces for -
    and removes non ascii characters.

    """

    text = utf8_to_unicode(text)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore')
    text = SLUG_INVALID_RE.sub('', text)
    text = unicode(text.strip())

    return SLUG_HYPENATE_RE.sub('-', text.lower())
