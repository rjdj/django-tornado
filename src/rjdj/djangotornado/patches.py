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

from tornado import escape

def patch_prepare(func):
    """Patches the Cookie header in the Tornado request to fulfull
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
