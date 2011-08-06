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

from paste.deploy.converters import asbool
from paste.deploy.config import ConfigMiddleware
from paste.registry import RegistryManager
from paste.cascade import Cascade
from paste.cgitb_catcher import CgitbMiddleware
from paste.evalexception import EvalException
from beaker.middleware import SessionMiddleware
from beaker.cache import CacheManager

from duende import get_enabled_app_list
from duende.lib import urls
from duende.lib.resource import get_resource_dir
from duende.lib.config import CONFIG
from duende.middleware.duendeapp import DuendeApplication
from duende.middleware.auth import AuthMiddleware
from duende.middleware.error import ErrorMiddleware
from duende.middleware.viewresolver import ViewResolverMiddleware
from duende.middleware.staticcontent import StaticContentMiddleware
from duende.middleware.flashmessage import FlashMessageMiddleware


def app_factory(global_config, **local_conf):
    """Create a WSGI application instance."""

    global CONFIG

    CONFIG.update_values(global_config.copy())
    CONFIG.update_values(local_conf)

    application = DuendeApplication(CONFIG)
    application = AuthMiddleware(application, CONFIG)
    application = ViewResolverMiddleware(application, CONFIG)
    application = FlashMessageMiddleware(application)
    application = RegistryManager(application)
    #application = ConfigMiddleware(application, CONFIG)
    application = SessionMiddleware(application, CONFIG)
    application = ErrorMiddleware(application, CONFIG)

    if asbool(CONFIG['debug']):
        if asbool(CONFIG.get('debug.multiprocess')):
            #This middleware supports multithread
            application = CgitbMiddleware(application, {'debug': True})
        else:
            #display errors to client when debug is enabled
            application = EvalException(application)

    return application


def static_app_factory(global_config, **local_conf):
    """Create an application instance to serve static contents."""

    config = global_config.copy()
    config.update(local_conf)
    #initialize mappings to be able to get enabled applications
    urls.init_application_urls(config['url.file'])

    application_list = []
    enabled_application_list = get_enabled_app_list()
    for app_name in enabled_application_list:
        static_app_dir = get_resource_dir(app_name)
        if not static_app_dir:
            #when resource dir does not exist continue with next app
            continue

        static_app_dir = os.sep.join([static_app_dir, 'static'])
        static_app = StaticContentMiddleware(static_app_dir,
                                             cache_max_age=None)
        application_list.append(static_app)

    #cascade all applications in order, so first static URL
    #are processed and then the other middlewares
    application = Cascade(application_list)

    return application
