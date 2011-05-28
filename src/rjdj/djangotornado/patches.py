##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# All Rights Reserved.
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
            self.request.headers[u'Cookie'] = escape.native_str(raw_cookie)
        return func(self)
    return inner_func

