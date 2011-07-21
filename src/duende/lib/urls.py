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

import urllib
import ConfigParser

from duende import CONFIG

__APP_URLS = {}


class URLMappingException(Exception):
    """Base class for URL mapping exceptions."""

    pass


def init_application_urls(url_file_name):
    """Init URL to application mapping object."""

    global __APP_URLS

    config = ConfigParser.ConfigParser()
    config.read(url_file_name)
    __APP_URLS.update(config.defaults())


def url_apply(url, *args, **kwargs):
    """Apply GET parameter to a URL

    A dictionary with parameter can be used as second argument.
    Parameters can also be given as keyword arguments.

    WARNING: This function might generate errors when using string replacement
    and some url quoted caracters, for example "-/" will be quoted as "-2%F"
    that is right but also is a valid python string replacement expression :).

    """

    if '?' not in url:
        url = url + '?'

    param_list = []
    param_dict = kwargs
    if args and isinstance(args[0], dict):
        param_dict.update(args[0])

    for (name, value) in param_dict.items():
        if isinstance(value, basestring) and value.startswith('%s'):
            #value is a python string sustitution variable so dont quote
            param = u'%s=%s' % (urllib.quote_plus(name), value)
        elif isinstance(value, (list, tuple)):
            for value_item in value:
                param_value = unicode(value_item)
                param = u'%s=%s' % (urllib.quote_plus(name),
                                    urllib.quote_plus(param_value))
                param_list.append(param)

            #after adding current list value items continuewith
            #next value in upper loop
            continue
        else:
            param_value = unicode(value)
            param = u'%s=%s' % (urllib.quote_plus(name),
                                urllib.quote_plus(param_value))

        param_list.append(param)

    params_string = u'&'.join(param_list)

    if url.endswith('?'):
        url = url + params_string
    else:
        #some parameters already exist in URL
        url = url + u'&' + params_string

    return url


def url(app_name, url):
    """Append URL prefix to given URL

    A list of arguments or keyword arguments can be given as parameters.
    Depending on the type of string subtitution used in the uri normal args
    or keyword args has to be used.

    """

    if app_name not in __APP_URLS:
        msg = u'Application %s not installed' % app_name

        raise URLMappingException(msg)

    prefix_url = CONFIG['url.prefix']
    full_url = prefix_url.rstrip('/') + __APP_URLS[app_name].rstrip('/') + url

    if args:
        full_url = full_url % args
    elif kwargs:
        full_url = full_url % kwargs

    return full_url


def get_url_mapping():
    """Get a dictionary with application to URL mappings."""

    if not __APP_URLS:
        msg = u'No app mappings available. Call init_application_urls() first.'

        raise URLMappingException(msg)

    mapping = {}
    mapping.update(__APP_URLS)

    return mapping


def get_url_app_mapping():
    """Get a dictionary with URL to application mappings."""

    mapping = get_url_mapping()
    for (app_name, url) in mapping.items():
        mapping[url.lstrip('/')] = app_name

    return mapping