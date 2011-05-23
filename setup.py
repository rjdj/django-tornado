import os
from setuptools import setup, find_packages

setup(name = "rjdj.djangotornado",
      version = "0.2.2",
      author = 'Reality Jockey Limited',
      author_email = 'developer@rjdj.me',
      description = 'Use Tornado with your Django project.',
      url = 'http://github.com/organizations/rjdj',
	  namespace_packages = ['rjdj'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      install_requires = ["distribute",
                          "Django"],
      entry_points = {
          'console_scripts':[]
          },
      include_package_data = False,
      zip_safe = False,
)
