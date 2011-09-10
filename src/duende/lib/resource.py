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
import logging
import mimetypes
import pkg_resources

from pkg_resources import require
from functools import partial
from paste import fileapp
from paste.util.import_string import try_import_module

from duende import httpexc

LOG = logging.getLogger(__name__)

#types that should be served as UTF8
UTF_TYPES = (
    'text/css',
    'application/x-javascript',
    'application/javascript',
    'text/html',
    'text/xml',
    'application/xml',
    'application/xhtml+xm',
    'text/plain',
    'text/csv',
)


def get_resource_dir(app_name):
    """Get directory where application resource files are located."""

    try:
        info = require(app_name)
    except pkg_resources.DistributionNotFound:
        #application is not installed so no resource is available
        return

    info = info[0]
    location = info.location
    #for namespaced applications replace dot by directory separator
    #to allow concatenation to access resources directory
    if '.' in app_name:
        app_name = app_name.replace('.', os.sep)

    dir = os.sep.join([location, app_name, 'resources'])
    if os.path.isdir(dir):
        return dir


def create_file_response(file_name):
    """Create a response to return a file."""

    (content_type, encoding) = mimetypes.guess_type(file_name)
    #set utf8 for known types
    if content_type in UTF_TYPES:
        content_type = content_type + '; charset=utf8'

    #TODO: Add caching information
    #headers = [
    #    ('Content-Type', content_type),
    #]

    return fileapp.FileApp(file_name, content_type=content_type)


def resource_handler(uri, request):
    """View to handle mapped resources."""

    LOG.debug(u'Resolving resource %s', uri)
    (protocol, resource) = uri.split(':')

    if protocol == 'url':
        #redirect to given URL
        raise httpexc.HTTPFound(location=uri)

    response = None
    if protocol == 'call':
        #get handler and call it with current request as parameter
        (module_path, view_name) = resource.split('#')
        module = try_import_module(module_path)
        view = getattr(module, view_name, None)
        if view:
            response = view(request)
    elif protocol == 'egg':
        #create a response with an iterator on resource file
        (app_name, file_path) = resource.split('#')
        resource_dir = get_resource_dir(app_name)
        if resource_dir:
            full_file_path = os.sep.join([resource_dir, file_path])
            if os.path.isfile(full_file_path):
                response = create_file_response(full_file_path)
            else:
                LOG.error(u'Invalid resource path: %s', full_file_path)
    else:
        LOG.error(u'Unknown resource URI: %s', uri)

    if not response:
        raise httpexc.HTTPNotFound()

    return response


def get_view_handler(uri):
    """Get a view handler for a resource uri."""

    fn = partial(resource_handler, uri)
    fn.__name__ = 'partial_resource_handler'
    fn.__doc__ = 'Partial resource_handler function for uri %s' % uri

    return fn
