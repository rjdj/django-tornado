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

import os
from setuptools import setup, find_packages

setup(name = "rjdj.djangotornado",
      version = "0.2.4",
      author = 'Reality Jockey Limited',
      author_email = 'developer@rjdj.me',
      description = 'Use Tornado with your Django project.',
      url = 'http://github.com/organizations/rjdj',
	  namespace_packages = ['rjdj'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      install_requires = ["distribute",
                          "Django",
                          "tornado",
                          ],
      entry_points = {
          'console_scripts': [],
          },
      include_package_data = False,
      zip_safe = False,
      extras_require = dict(test = ['zope.testing','webtest']),
)
