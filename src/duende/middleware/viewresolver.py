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
import logging

from webob import Request
from paste.util.import_string import try_import_module
from paste.deploy.converters import asbool

from duende import REQUEST
from duende import httpexc
from duende import get_enabled_app_list
from duende.lib import jsonrpc
from duende.lib import urls

LOG = logging.getLogger(__name__)

#regex to replace invalid URL characters
RE_INVALID_URL_CHARS = re.compile(ur'[^a-zA-Z0-9]')


class URLParseError(Exception):
    """Exception raised when parsing an URL with invalid format"""

    message = u'Wrong URL format'


def get_view_module_parts(url):
    """Parse a URL and return a tuple with view module path info

    Function return a 3-tuple with application name, path to module where
    view is defined and the name of the view that will handle given URL.
    Non alphanumeric characters are removed from URL, with exception of
    view name that will use an underscore '_' where a non alphanumeric
    character is found.
    All characters will be tranformed to lowercase.
    When no module name is available in URL "root" s used as module name.

    A tipical URL like:
        /app-name/path-to/module-name/view-name/
    will result in:
        (u'appname', u'pathto.modulename', u'view_name')

    """

    #tidy URL before processing
    url = url.strip(u'/')
    url = url.lower()

    url_path_list = url.split(u'/')
    if len(url_path_list) < 2:
        raise URLParseError()

    view_name = url_path_list[-1]
    #replace invalid URL chars with underscore
    view_name = RE_INVALID_URL_CHARS.sub(u'_', view_name)

    #remove view name from list and leave only valid
    #charactes for each name in URL path
    url_path_list = url_path_list[:-1]
    url_path_list = [RE_INVALID_URL_CHARS.sub(u'', name) \
                     for name in url_path_list]

    #get app name and path to module where view
    #for current URL is located
    app_name = url_path_list[0]
    module_path = u'.'.join(url_path_list[1:])
    if not module_path:
        #when no module path is available use
        #name for default module
        module_path = u'root'

    return (app_name, module_path, view_name)


class ViewResolverMiddleware:
    """Middleware in charge of resolving URL to view"""

    def __init__(self, config):
        self.config = config
        urls.init_application_urls(config['url.file'])
        self.enabled_app_list = get_enabled_app_list()
        self.url_app_mapping = urls.get_url_app_mapping()

    def __call__(self, environ, start_response):
        config = self.config
        debug_enabled = asbool(self.config['debug'])

        LOG.debug(u'Resolving view handler')
        try:
            view_handler = self.resolve_view_handler()
            response = view_handler(REQUEST)
        except httpexc.HTTPException, exc:
            #on HTTP errors create a proper response from exception
            response = REQUEST.get_response(exc)
        except Exception:
            LOG.exception(u'Unable to get response')
            #when debugging raise error
            if debug_enabled:
                raise

            #when JSON-RPC is used return JSON result
            http_requested_with = REQUEST.headers['X-Requested-With']
            is_xmlhttp = (http_requested_with == 'XMLHttpRequest')
            if is_xmlhttp and REQUEST.headers['Accept'] == 'application/json':
                err = jsonrpc.JSONInternalError()
                response = jsonrpc.get_reponse(err)
            else:
                #TODO: Display nice internal server error page
                err = httpexc.HTTPInternalServerError()
                response = REQUEST.get_response(exc)

        if debug_enabled and asbool(config.get('debug.requests', 'false')):
            #log request status and URL
            LOG.error(u'[%s] %s', response.status, REQUEST.url)

        return response(environ, start_response)

    def resolve_view_handler(self):
        """Get view handler for current request"""

        view = None
        #initialize module path for view handler
        url = REQUEST.path_info
        if url == '/' or not url:
            url = self.config['url.default']

        try:
            (app_name, module_path, view_name) = get_view_module_parts(url)
        except URLParseError:
            LOG.error(u'Unable get view handler for URL %s', url)

            raise httpexc.HTTPNotFound()

        #get name of application module for current url application name
        app_module_name = self.url_app_mapping.get(app_name)

        #first check for non namespaced enabled application names
        disabled_app = (app_module_name not in self.enabled_app_list)

        #view name can't start with underscore
        if view_name.startswith('_') or disabled_app:
            raise httpexc.HTTPNotFound()

        module_path = '%s.view.%s' % (app_module_name, module_path)
        LOG.debug(u'Request view module: %s', module_path)

        #import view module and get handler
        module = try_import_module(module_path)
        view = getattr(module, view_name, None)
        #check that current view definition is part of module (is not imported)
        if not view or (getattr(view, '__module__', None) != module.__name__):
            #when handler is not found raise HTTP 404
            raise httpexc.HTTPNotFound()

        #store current application name inside request
        REQUEST.environ['duende.application'] = app_module_name

        return view
