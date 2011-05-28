##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# All Rights Reserved.
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
