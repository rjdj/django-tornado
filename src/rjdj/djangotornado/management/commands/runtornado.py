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

import os
import sys

import logging

import django
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.management.base import BaseCommand, CommandError

from tornado import wsgi, httpserver, ioloop
from tornado.options import parse_command_line
from tornado.web import Application, RequestHandler, FallbackHandler, URLSpec

from rjdj.djangotornado import patches
from rjdj.djangotornado.signals import tornado_exit
from rjdj.djangotornado.shortcuts import set_application


logger = logging.getLogger()

class WelcomeHandler(RequestHandler):

    def get(self):
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        self.write("Tornado Web Server with Django %s" % django.get_version())
        self.finish()


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = "Starts a single threaded Tornado web server."
    args = '[optional port number, or ipaddr:port]'

    can_import_settings = True

    def handle(self, addrport='', *args, **options):
        """Handle command call"""

        if args:
            raise CommandError('Usage is runtornado %s' % self.args)
        if not addrport:
            self.addr = ''
            self.port = '8000'
        else:
            try:
                self.addr, self.port = addrport.split(':')
            except ValueError:
                self.addr, self.port = '', addrport
        if not self.addr:
            self.addr = '127.0.0.1'

        if not self.port.isdigit():
            raise CommandError("%s is not a valid port number." % port)

        self.quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        self.inner_run()

    def get_handler(self, *args, **kwargs):
        """Return Tornado application with Django WSGI handlers"""

        # Patch prepare method from Tornado's FallbackHandler
        FallbackHandler.prepare = patches.patch_prepare(FallbackHandler.prepare)

        django_app = wsgi.WSGIContainer(WSGIHandler())
        handlers = (
            URLSpec(r'/_', WelcomeHandler),
            URLSpec(r'.*', FallbackHandler, dict(fallback=django_app)),
        )
        opts = {
            "debug": settings.DEBUG,
            "loglevel": settings.DEBUG and "debug" or "warn",
        }
        return Application(handlers, **opts)

    def run(self, *args, **options):
        """Run application either with or without autoreload"""
        self.inner_run()

    def inner_run(self):
        """Get handler and start IOLoop"""
        parse_command_line()
        logger.info("Validating models...")
        self.validate(display_num_errors=True)
        logger.info("\nDjango version %(version)s, using settings %(settings)r\n"
                   "Server is running at http://%(addr)s:%(port)s/\n"
                   "Quit the server with %(quit_command)s.\n" % {
                       "version": self.get_version(),
                       "settings": settings.SETTINGS_MODULE,
                       "addr": self.addr,
                       "port": self.port,
                       "quit_command": self.quit_command,
                   })

        app = self.get_handler()
        set_application(app)

        server = httpserver.HTTPServer(app)
        server.listen(int(self.port), address=self.addr)
        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            logger.warn("Shutting down Tornado ...")
        finally:
            tornado_exit.send_robust(sender=self)
            sys.exit(0)
