##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# This file is part of django-tornado.
#
# Django-tornado is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Django-tornado is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-tornado. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# -*- coding: utf-8 -*-

__docformat__ = "reStructuredText"

import re
import logging

from tornado import escape
from tornado.web import Application, URLSpec

def patch_prepare(func):
    """Patches the Cookie header in the Tornado request to fulfill
    Django's strict string-type cookie policy"""
    def inner_func(self,**kwargs):
        if u'Cookie' in self.request.headers:
            raw_cookie = self.request.headers[u'Cookie']
            if isinstance(raw_cookie, unicode):
                if hasattr(escape,"native_str"):
                    self.request.headers[u'Cookie'] = escape.native_str(raw_cookie)
                else:
                    print "Method 'native_str' in module 'escape' not found."
                    self.request.headers[u'Cookie'] = str(raw_cookie)
        return func(self)
    return inner_func


class DjangoApplication(Application):

    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to our handler list.

        Note that host patterns are processed sequentially in the
        order they were added, and only the first matching pattern is
        used.  This means that all handlers for a given host must be
        added in a single add_handlers call.
        """
        if not host_pattern.endswith("$"):
            host_pattern += "$"
        handlers = []
        # The handlers with the wildcard host_pattern are a special
        # case - they're added in the constructor but should have lower
        # precedence than the more-precise handlers added later.
        # If a wildcard handler group exists, it should always be last
        # in the list, so insert new groups just before it.
        if self.handlers and self.handlers[-1][0].pattern == '.*$':
            self.handlers.insert(-1, (re.compile(host_pattern), handlers))
        else:
            self.handlers.append((re.compile(host_pattern), handlers))

        for spec in host_handlers:
            if type(spec) is type(()):
                assert len(spec) in (2, 3)
                pattern = spec[0]
                handler = spec[1]

                if isinstance(handler, str):
                    # import the Module and instantiate the class
                    # Must be a fully qualified name (module.ClassName)
                    handler = import_object(handler)

                if len(spec) == 3:
                    kwargs = spec[2]
                else:
                    kwargs = {}
                spec = URLSpec(pattern, handler, kwargs)
            handlers.append(spec)
            handler_name = spec.kwargs.get("handler_name", spec.name)
            if handler_name:
                if handler_name in self.named_handlers:
                    logging.warning(
                        "Multiple handlers named %s; replacing previous value",
                        handler_name)
                self.named_handlers[handler_name] = spec
