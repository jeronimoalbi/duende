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

import logging
import mimetypes

from functools import wraps

from jinja2 import Environment
from jinja2 import PrefixLoader
from jinja2 import PackageLoader
from jinja2 import TemplateNotFound
from jinja2 import FileSystemBytecodeCache
from jinja2 import nodes
from jinja2.utils import Markup
from jinja2.utils import contextfunction
from jinja2.ext import InternationalizationExtension
from paste.deploy.converters import asbool

from duende import REQUEST
from duende import Response
from duende import get_enabled_app_list
from duende.lib import flash
from duende.lib import urls

LOG = logging.getLogger(__name__)

ENVIRON = None


class TemplateException(Exception):
    pass


class TemplateRenderException(TemplateException):
    pass


@contextfunction
def _gettext_alias(context, *args, **kwargs):
    arg_count = len(args)
    if arg_count == 1:
        #when domain is not given get it from context name
        domain = context.name.split('/')[0]
        message = args[0]
    elif arg_count == 2:
        #args must be (message, domain) tuple
        (message, domain) = args
    else:
        raise TemplateException(u'Invalid arguments for _ function')

    new_args = (domain, message)
    gettext = context.resolve('gettext')

    return context.call(gettext, *new_args, **kwargs)


def _make_new_gettext(func):
    @contextfunction
    def gettext(context, domain, string, **variables):
        rv = context.call(func, domain, string)
        if context.eval_ctx.autoescape:
            rv = Markup(rv)

        return rv % variables

    return gettext


def _make_new_ngettext(func):
    @contextfunction
    def ngettext(context, domain, singular, plural, num, **variables):
        variables.setdefault('num', num)
        rv = context.call(func, domain, singular, plural, num)
        if context.eval_ctx.autoescape:
            rv = Markup(rv)

        return rv % variables

    return ngettext


class I18NDomainExtension(InternationalizationExtension):
    """Jinja2 extension to allow using domains in template translation"""

    def __init__(self, environment):
        super(I18NDomainExtension, self).__init__(environment)
        environment.globals['_'] = _gettext_alias

    def parse(self, parser):
        """Parse a translatable tag."""

        lineno = next(parser.stream).lineno
        num_called_num = False
        #application name is the first item in template name path
        domain = parser.name.split('/')[0]

        # find all the variables referenced.  Additionally a variable can be
        # defined in the body of the trans block too, but this is checked at
        # a later state.
        plural_expr = None
        variables = {}
        while parser.stream.current.type != 'block_end':
            if variables:
                parser.stream.expect('comma')

            # skip colon for python compatibility
            if parser.stream.skip_if('colon'):
                break

            name = parser.stream.expect('name')
            if name.value in variables:
                parser.fail('translatable variable %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)

            # expressions
            if parser.stream.current.type == 'assign':
                next(parser.stream)
                variables[name.value] = var = parser.parse_expression()
            else:
                variables[name.value] = var = nodes.Name(name.value, 'load')

            if plural_expr is None:
                plural_expr = var
                num_called_num = name.value == 'num'

        parser.stream.expect('block_end')

        plural = plural_names = None
        have_plural = False
        referenced = set()

        # now parse until endtrans or pluralize
        singular_names, singular = self._parse_block(parser, True)
        if singular_names:
            referenced.update(singular_names)
            if plural_expr is None:
                plural_expr = nodes.Name(singular_names[0], 'load')
                num_called_num = singular_names[0] == 'num'

        # if we have a pluralize block, we parse that too
        if parser.stream.current.test('name:pluralize'):
            have_plural = True
            next(parser.stream)
            if parser.stream.current.type != 'block_end':
                name = parser.stream.expect('name')
                if name.value not in variables:
                    parser.fail('unknown variable %r for pluralization' %
                                name.value, name.lineno,
                                exc=TemplateAssertionError)
                plural_expr = variables[name.value]
                num_called_num = name.value == 'num'
            parser.stream.expect('block_end')
            plural_names, plural = self._parse_block(parser, False)
            next(parser.stream)
            referenced.update(plural_names)
        else:
            next(parser.stream)

        # register free names as simple name expressions
        for var in referenced:
            if var not in variables:
                variables[var] = nodes.Name(var, 'load')

        if not have_plural:
            plural_expr = None
        elif plural_expr is None:
            parser.fail('pluralize without variables', lineno)

        node = self._make_node(domain, singular, plural, variables,
                               plural_expr,
                               bool(referenced),
                               num_called_num and have_plural)
        node.set_lineno(lineno)

        return node

    def _install(self, translations, newstyle=None):
        msg = u'Not supported method install_gettext_translations'

        raise TemplateException(msg)

    def _install_callables(self, gettext, ngettext, newstyle=None):
        if newstyle is not None:
            self.environment.newstyle_gettext = newstyle
        if self.environment.newstyle_gettext:
            gettext = _make_new_gettext(gettext)
            ngettext = _make_new_ngettext(ngettext)
        self.environment.globals.update(
            gettext=gettext,
            ngettext=ngettext
        )

    def _make_node(self, domain, singular, plural, variables, plural_expr,
                   vars_referenced, num_called_num):
        """Generates a useful node from the data provided."""

        # no variables referenced?  no need to escape for old style
        # gettext invocations only if there are vars.
        if not vars_referenced and not self.environment.newstyle_gettext:
            singular = singular.replace('%%', '%')
            if plural:
                plural = plural.replace('%%', '%')

        # singular only:
        if plural_expr is None:
            gettext = nodes.Name('gettext', 'load')
            node = nodes.Call(gettext, [
                nodes.Const(domain),
                nodes.Const(singular)
            ], [], None, None)

        # singular and plural
        else:
            ngettext = nodes.Name('ngettext', 'load')
            node = nodes.Call(ngettext, [
                nodes.Const(domain),
                nodes.Const(singular),
                nodes.Const(plural),
                plural_expr
            ], [], None, None)

        # in case newstyle gettext is used, the method is powerful
        # enough to handle the variable expansion and autoescape
        # handling itself
        if self.environment.newstyle_gettext:
            for key, value in variables.iteritems():
                # the function adds that later anyways in case num was
                # called num, so just skip it.
                if num_called_num and key == 'num':
                    continue
                node.kwargs.append(nodes.Keyword(key, value))

        # otherwise do that here
        else:
            # mark the return value as safe if we are in an
            # environment with autoescaping turned on
            node = nodes.MarkSafeIfAutoescape(node)
            if variables:
                node = nodes.Mod(node, nodes.Dict([
                    nodes.Pair(nodes.Const(key), value)
                    for key, value in variables.items()
                ]))
        return nodes.Output([node])


i18n = I18NDomainExtension


def template(template_name):
    """Decorator to return a request based on a template output

    View handlres has to return a dictionary that will be used to initialize
    template variables.
    If None is returned then no variables will be assigned to template.
    To override given template a context variable named _template can be
    given with the new template name to use.

    Usage:

        @template('tests/test_template.html')
        def view_handler(*args, **kwargs):
            result = {}
            result['variable'] = 'Hola Mundo !'

            return result

    """

    def _template(func):
        @wraps(func)
        def _template_wrap(*args, **kwargs):
            context = func(*args, **kwargs)
            #check that a valid value was returned by view
            if not isinstance(context, dict) and context is not None:
                msg = u'View handler must return a dict or None'

                raise TemplateRenderException(msg)

            #if a template name is given use it instead current template name
            if context is not None and '_template' in context:
                _template = context['_template']
                tpl_text = render(REQUEST, _template, context=context)
            else:
                tpl_text = render(REQUEST, template_name, context=context)
            #get mime type from template name
            (mime_type, encoding) = mimetypes.guess_type(template_name)
            if not encoding:
                encoding = 'utf8'

            if not mime_type:
                msg = u'Unrecognized mime type for template %s' % template_name

                raise TemplateRenderException(msg)

            #create response for current template
            response = Response()
            response.headers['Content-Type'] = mime_type
            response.charset = encoding
            response.unicode_body = tpl_text

            return response

        return _template_wrap

    return _template


def render(request, template_name, context=None):
    """Get template contents."""

    if not context:
        context = {}

    if not isinstance(context, dict):
        msg = u'Invalid context value. Context must be dict or None'

        raise TemplateRenderException(msg)

    #init environment for current request
    env = context['env'] = {}
    #add flash object when available
    if 'duende.flash' in request.environ:
        env['flash'] = request.environ['duende.flash']
    else:
        LOG.info(u'Flash is not enabled')

    LOG.debug(u'Rendering template name %s', template_name)
    template = ENVIRON.get_template(template_name)

    return template.render(**context)


def init_template_environment(config):
    """Initialize template support"""

    global ENVIRON

    enabled_app_list = get_enabled_app_list()
    #add a template loader for each application
    mapping_dict = {}
    for app_name in enabled_app_list:
        path = 'resources/templates'
        mapping_dict[app_name] = PackageLoader(app_name, package_path=path)

    loader = PrefixLoader(mapping_dict)
    bytecode_cache = FileSystemBytecodeCache(config['template.cache_dir'],
                                             '%s.cache')

    environ_params = {}
    environ_params['extensions'] = ['duende.lib.template.i18n']
    environ_params['trim_blocks'] = True
    environ_params['loader'] = loader
    environ_params['bytecode_cache'] = bytecode_cache
    ENVIRON = Environment(**environ_params)

    #TODO: Allow apps to add context values
    context = {}
    context['url'] = urls.url
    context['DEBUG'] = asbool(config['debug'])

    #update template environment
    ENVIRON.globals.update(context)
