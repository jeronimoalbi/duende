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

from paste.util.import_string import try_import_module
from paste.deploy.converters import asbool

from duende import httpexc
from duende import get_enabled_app_list
from duende.lib import jsonrpc
from duende.lib import urls
from duende.lib import resource

LOG = logging.getLogger(__name__)

#regex to replace invalid URL characters
RE_INVALID_URL_CHARS = re.compile(ur'[^a-zA-Z0-9]')


class URLParseError(Exception):
    """Exception raised when parsing an URL with invalid format"""

    def __str__(self):
        return 'Wrong URL format'


class ViewResolverMiddleware:
    """Middleware in charge of resolving URL to view"""

    def __init__(self, application, config):
        self.application = application
        self.config = config
        self.enabled_app_list = get_enabled_app_list()
        self.url_app_mapping = urls.get_url_app_mapping()
        self.resource_mapping = urls.get_resource_mapping()

    def __call__(self, environ, start_response):
        view_handler = self.resolve_view_handler(environ)
        environ['duende.view'] = view_handler

        return self.application(environ, start_response)

    def resolve_view_handler(self, environ):
        """Get view handler for current request"""

        LOG.debug(u'Resolving view handler')
        view = None
        #tidy URL before processing
        url = environ['PATH_INFO'].strip(u'/')
        url = url.lower()

        #check if its a resource
        if url in self.resource_mapping:
            resource_uri = self.resource_mapping[url]

            return resource.get_view_handler(resource_uri)

        try:
            (app, module_path, view_name) = self.get_view_module_parts(url)
        except URLParseError:
            LOG.error(u'Unable get view handler for URL /%s', url)

            raise httpexc.HTTPNotFound()

        module_path = '%s.view.%s' % (app, module_path)
        LOG.debug(u'Request view: %s.%s()', module_path, view_name)

        #import view module and get handler
        module = try_import_module(module_path)
        view = getattr(module, view_name, None)
        #check that current view definition is part of module (is not imported)
        if not view or (getattr(view, '__module__', None) != module.__name__):
            #when handler is not found raise HTTP 404
            raise httpexc.HTTPNotFound()

        #store current application name inside environment
        environ['duende.application'] = app

        return view

    def get_view_module_parts(self, url):
        """Parse a URL and return a tuple with view module path info

        Function return a 3-tuple with app module name, path to module where
        view is defined and the name of the view that will handle given URL.
        Non alphanumeric characters are removed from URL, with exception of
        view name that will use an underscore '_' where a non alphanumeric
        character is found.
        All characters will be tranformed to lowercase.
        When no module name is available in URL "root" s used as module name.

        A tipical URL like:
            /app/path-to/module-name/view-name/
        will result in:
            (u'app', u'pathto.modulename', u'view_name')

        """

        #set default return values
        app = root_app = self.url_app_mapping.get('/')
        module_path = 'root'
        view_name = 'index'
        url_path_list = []

        if url:
            url_path_list = url.split(u'/')

        url_path_count = len(url_path_list)
        #get view name when URL has at least one path element
        if url_path_count:
            #TODO: when count is 1 check if view_name is an app ?
            view_name = url_path_list[-1]
            #view name can't start with underscore
            if view_name.startswith('_'):
                raise httpexc.HTTPNotFound()

            #replace invalid URL chars with underscore
            view_name = RE_INVALID_URL_CHARS.sub(u'_', view_name)

        #get the reast of the URL elements
        if url_path_count > 1:
            #remove view name from list and leave only valid
            #charactes for each name in URL path
            url_path_list = url_path_list[:-1]
            url_path_list = [RE_INVALID_URL_CHARS.sub(u'', name) \
                             for name in url_path_list]

            #init base app URL
            base_app_url = url_path_list[0]
            #get name of application module for current url application name
            app = self.url_app_mapping.get(base_app_url)
            #when and app for URL does not exist use root application URL
            if app not in self.enabled_app_list:
                #get root application
                app = root_app
                #get path to module where view for current URL is located
                module_path = u'.'.join(url_path_list)
            elif url_path_count > 2:
                #set module path only when is available in URL
                module_path = u'.'.join(url_path_list[1:])

        return (app, module_path, view_name)
