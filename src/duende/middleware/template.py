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

from duende.middleware import MiddlewareException
from duende.lib import template
from duende.lib.i18n import translation


class TemplateMiddleware:
    """Middleware to initialize Jinja2 template support."""

    def __init__(self, application, config):
        self.application = application
        self.config = config
        template.init_template_environment(config)

    def __call__(self, environ, start_response):
        if 'duende.translation' not in environ:
            msg = u'No translation initialized. LocaleMiddleware missing ?'

            raise MiddlewareException(msg)

        gettext = translation.dgettext
        ngettext = translation.dngettext
        tpl_env = template.ENVIRON
        tpl_env.install_gettext_callables(gettext, ngettext, newstyle=True)

        return self.application(environ, start_response)
