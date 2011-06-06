_Copyright &copy; 2011 Reality Jockey Ltd. and Contributors._

_This file is part of django-tornado._

_Django-tornado is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. Django-tornado is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details._

_You should have received a copy of the GNU Lesser General Public License along with django-tornado. If not, see <http://www.gnu.org/licenses/>._


Run Tornado Web Server with Django
==================================

Acknowledgement
---------------

This package is based upon ideas and code snippets from:

  - https://github.com/koblas/django-on-tornado/blob/master/myproject/django_tornado/management/commands/runtornado.py

which is also based on:

  - http://geekscrap.com/2010/02/integrate-tornado-in-django/


Installation with Buildout
--------------------------

  - Add "rjdj.djangotornado" to your requirements in setup.py

  - Add "rjdj.djangotornado" to INSTALLED_APPS in your Django settings.py

  - Make sure you have the "tornado" package in your sys.path


Example configuration with Buildout
-----------------------------------

*buildout.cfg* (excerpt)

    [buildout]
    find-links = http://download.rjdj.me/python

    [versions]
    Django=1.3
    zc.buildout=1.5.2
    rjdj.djangotornado=0.1

    [instance]
    recipe = zc.recipe.egg:script
    eggs = rjdj.camp
    scripts = instance
    extra-paths = ${tornado:location}
    arguments = settings
    initialization = from my.project import settings
    
    [tornado]
    recipe = minitage.recipe.fetch
    urls = git://github.com/facebook/tornado.git | git | | ${buildout:parts-directory}/tornado

*setup.py* (excerpt)

    setup(name = "my.project",
          version = "0.0.1",
          author = '',
          author_email = '',
          description = 'My Django Project with Tornado',
          url = '',
    	  namespace_packages = [],
          packages = find_packages('src'),
          package_dir = {'':'src'},
          install_requires = ['Django',
                              'rjdj.djangotornado',
                             ],
          entry_points = {
              'console_scripts':['instance=django.core.management:execute_manager']
              },
          include_package_data = True,
          zip_safe = False,
          extras_require = dict(instance=[]),
    )

####GitHub Repository:

    git://github.com/rjdj/django-tornado.git
