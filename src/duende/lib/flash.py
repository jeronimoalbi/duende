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

from duende import REQUEST

# Flash message types
INFO = 'info'
ERROR = 'error'
SUCCESS = 'success'
WARNING = 'warning'


class Flash(object):
    """Class to handle flash messages"""

    def __init__(self, session_manager):
        self._session = session_manager

        if 'flash' not in self._session:
            self._session['flash'] = {}

        self._flash = self._session['flash']

        if 'message_list' in self._flash:
            #copy message list from session
            self._message_list = self._flash['message_list'][:]
        else:
            self._message_list = []

        if 'messages_type' in self._flash:
            self._messages_type = self._flash['messages_type']
        else:
            self._messages_type = INFO

        #clear session messages
        self._flash['message_list'] = []
        #clear type from session
        self._flash['messages_type'] = INFO

    def get_message_list(self):
        for message in self._message_list:
            yield message

    def get_messages_type(self):
        return self._messages_type

    def set_messages_type(self, messages_type):
        self._messages_type = messages_type
        self._flash['messages_type'] = messages_type

    def get_display_message_count(self):
        """Get the number of messages to display"""

        return len(self._message_list)

    def add_message(self, message, message_type=None):
        self._flash['message_list'].append(message)
        #TODO: Implement type by message instead of global type
        if message_type:
            self.messages_type = message_type

    def clear(self):
        """Clear display and session messages"""

        self._message_list = []
        self._flash['message_list'] = []

    message_list = property(get_message_list)
    messages_type = property(get_messages_type, set_messages_type)
    display_message_count = property(get_display_message_count)


def get_message_list():
    """Get a list with current request messages"""

    flash = REQUEST.environ['duende.flash']

    return [message for message in flash.get_message_list()]


def add_message(message, message_type=None):
    """Add a flash message"""

    flash = REQUEST.environ['duende.flash']
    flash.add_message(message, message_type=message_type)


def clear_messages():
    """Clear all flash messages"""

    REQUEST.environ['duende.flash'].clear()


def set_type(messages_type):
    """Set type for all messages"""

    REQUEST.environ['duende.flash'].messages_type = messages_type
