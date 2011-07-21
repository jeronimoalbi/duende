# -*- coding: utf8 -*-
#
# Copyright (c) 2011, Jerónimo José Albi <jeronim.oalbi@gmail.com>
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

from paste.script.templates import Template
from paste.script.templates import var

import duende

DUENDE_VERSION = duende.__version__
TEMPLATES_DIR = '../resources/paste_templates/'
VARS = [
    var('version', '0.0.1', default='0.0.1'),
    var('description', 'One-line description of the package'),
    var('author', 'Author name'),
    var('author_email', 'Author email'),
    var('zip_safe', 'True/False: package can be distributed as a .zip file',
        default=False),
    var('duende_version', DUENDE_VERSION, default=DUENDE_VERSION),
]


class DuendeProjectTemplate(Template):
    """Class to handle creation of duende applications"""

    _template_dir = TEMPLATES_DIR + 'duende'
    summary = 'Template for creating a Duende application'
    required_templates = []
    vars = VARS
