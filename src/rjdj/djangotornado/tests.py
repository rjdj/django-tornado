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

import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite


class CustomTestLayer(object):

    @classmethod
    def setUp(self):
        pass

    @classmethod
    def tearDown(self):
        pass

    @classmethod
    def testSetUp(self):
        pass

    @classmethod
    def testTearDown(self):
        pass


def test_suite():
    """Return Test Suite"""
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    testing = DocFileSuite('testing.txt', optionflags=optionflags)
    handlers = DocFileSuite('handlers.txt', optionflags=optionflags)
    suite = unittest.TestSuite((testing,handlers,))
    suite.layer = CustomTestLayer
    return suite
