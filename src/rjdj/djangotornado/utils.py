##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# All Rights Reserved.
#
##############################################################################

# -*- coding: utf-8 -*-

__docformat__ = "reStructuredText"

import os
import sys

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

def stdprint(self, *args, **kwargs):
    """Print in color to stdout"""
    text = " ".join([str(item) for item in args])
    color = kwargs.get("color",32)
    sys.stdout.write("\033[0;%dm%s\033[0;m" % (color, text))
