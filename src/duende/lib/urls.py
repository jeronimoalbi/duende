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

import ConfigParser
import logging
import re
import unicodedata
import urllib
import urlparse

from duende.lib.config import CONFIG

LOG = logging.getLogger(__name__)

#slugify regexps
SLUG_INVALID_RE = re.compile(r'[^\w\s-]')
SLUG_HYPENATE_RE = re.compile(r'[-\s]+')

_MAPPINGS = {}


class URLException(Exception):
    """Base class for URL exceptions."""

    pass


class URLMappingException(URLException):
    """Base class for URL mapping exceptions."""

    pass


def init_application_urls(url_file_name):
    """Init URL to application mapping object."""

    global _MAPPINGS

    _MAPPINGS['url'] = {}
    _MAPPINGS['resource'] = {}


    LOG.debug(u'Initializing application url mappings')
    config = ConfigParser.ConfigParser()
    config.read(url_file_name)

    sections = config.sections()

    if 'apps' not in sections:
        msg = u'No applications mapped in url file'

        raise URLMappingException(msg)

    for (app_name, url) in config.items('apps'):
        _MAPPINGS['url'][app_name] = unicode(url, 'utf8')

    #check that a root application is available
    if '/' not in _MAPPINGS['url'].values():
        msg = u'No root application mapped in url file'

        raise URLMappingException(msg)

    if 'resources' in sections:
        for (resource_name, uri) in config.items('resources'):
            _MAPPINGS['resource'][unicode(resource_name, 'utf8')] = uri


def url_apply(url, *args, **kwargs):
    """Apply parameters to a URL

    A dictionary with parameters can be used as second argument.
    Parameters can also be given as keyword arguments.

    WARNING: This function might generate errors when using string replacement
    and some url quoted caracters, for example "-/" will be quoted as "-2%F"
    that is right but also is a valid python string replacement expression :).

    """

    if '?' not in url:
        url = url + u'?'

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


def url(url, *args, **kwargs):
    """Append URL prefix to given URL

    A list of arguments or keyword arguments can be given as parameters.
    Depending on the type of string subtitution used in the uri normal args
    or keyword args has to be used.

    URL can be a normal or relative, as well as an application uri
    like app_name:app_relative_url.

    """

    #dont parse full URL
    if '://' in url:
        return url

    prefix_url = CONFIG['url.prefix']
    prefix_url = unicode(prefix_url).rstrip('/')

    #check if URL is an application URI
    if ':' in url and not url.startswith('/'):
        try:
            (app_name, relative_url) = url.split(':')
        except ValueError:
            raise URLException(u'Invalid app url format')

        if app_name not in _MAPPINGS['url']:
            msg = u'Application %s not installed' % app_name

            raise URLMappingException(msg)

        app_url = _MAPPINGS['url'][app_name].rstrip('/')
        full_url = prefix_url + app_url + relative_url
    else:
        #just add prefix to given url
        full_url = prefix_url + url

    if args:
        full_url = full_url % args
    elif kwargs:
        full_url = full_url % kwargs

    return full_url


def get_url_mapping():
    """Get a dictionary with application to URL mappings."""

    if not _MAPPINGS['url']:
        msg = u'No app mappings available. Call init_application_urls() first.'

        raise URLMappingException(msg)

    mapping = {}
    mapping.update(_MAPPINGS['url'])

    return mapping


def get_url_app_mapping():
    """Get a dictionary with URL to application mappings."""

    mapping = get_url_mapping()
    for (app_name, base_url) in mapping.items():
        url = (base_url if base_url == '/' else base_url.lstrip('/'))
        mapping[url] = app_name

    return mapping


def get_resource_mapping():
    """Get a dictionary with resource mappings."""

    mapping = {}
    mapping.update(_MAPPINGS['resource'])

    return mapping


def slugify(text):
    """Convert any string to a safe ASCII string

    It can be used for file names that can have
    invalid characters and also for URLs.

    """

    if not isinstance(text, unicode):
        text = unicode(text)

    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore')
    text = SLUG_INVALID_RE.sub('', text)
    text = unicode(text.strip())

    return SLUG_HYPENATE_RE.sub('-', text.lower())


def url_quote(url):
    """Quote a URL that has unicode characters in path and param names

    Return a unicode.

    """

    if not isinstance(url, unicode):
        url = unicode(url)

    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)

    #TODO: Check if is good to let it fail
    path = path.encode('utf8', 'ignore')
    path = unicode(urllib.quote(path))
    query = query.encode('utf8')
    query = unicode(urllib.quote(query, '=&/'))

    url_parts = (scheme, netloc, path, query, fragment)

    return urlparse.urlunsplit(url_parts)


def url_unquote(url):
    """Unquote a URL that was quoted using url_quote

    Return a unicode.

    """

    if not isinstance(url, unicode):
        url = unicode(url)

    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)

    path = path.encode('utf8')
    path = unicode(urllib.unquote(path), 'utf8')
    query = query.encode('utf8')
    query = unicode(urllib.unquote(query), 'utf8')

    url_parts = (scheme, netloc, path, query, fragment)

    return urlparse.urlunsplit(url_parts)
