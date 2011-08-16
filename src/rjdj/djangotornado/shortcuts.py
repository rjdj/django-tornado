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

from threading import Lock

current_application = None
lock = Lock()

def set_application(app):
    global lock
    global current_application
    
    lock.acquire()
    current_application = app
    lock.release()

def reverse(django_view, *args):
    """ Shortcuts the reverse lookup of views in the application """
    
    global current_application
    
    if not current_application:
        raise ValueError("No application found!")
    if not hasattr(django_view, "__name__"):
        raise ValueError("Invalid view function")
        
    return current_application.reverse_url(django_view.__name__, *args)
