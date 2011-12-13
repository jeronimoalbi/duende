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
import code
import os
import sys

from paste.deploy import loadapp

BANNER = "Duende interactive console"


class SimpleConsole(code.InteractiveConsole):
    """Simple python console."""
    def __call__(self, header=""):
        try:
            import readline
        except ImportError:
            print("warning: Module readline not available. Command "
                  "line history and completion won't be available.")
        
        self.interact(header)


def shell():
    """Initialize an interactive shell for Duende.

    When a config file is not given as argument duende.ini will
    be used as default.

    Example:
        # paster shell duende.ini

    """
    if len(sys.argv) < 2:
        config_file = 'duende.ini'
    else:
        config_file = sys.argv[1]

    config_path = os.path.abspath(config_file)
    if not os.path.isfile(config_path):
        raise Exception(u'Config file %s not found' % config_path)

    cur_dir = os.path.dirname(config_path)
    if cur_dir not in sys.path:
        sys.path.insert(0, cur_dir)

    print("Loading duende app config from {0}".format(config_path))
    config_key = 'config:%s' % config_path
    wsgiapp = loadapp(config_key)

    try:
        import IPython

        if IPython.__version__ < '0.11':
            from IPython.Shell import IPShellEmbed

            shell = IPShellEmbed(['-quick'])
        else:
            from IPython import embed as shell
    except ImportError:
        # when ipython is not installed use normal console
        shell = SimpleConsole()
        
    shell(header=BANNER)
