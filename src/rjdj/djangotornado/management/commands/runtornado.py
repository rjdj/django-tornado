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

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from tornado.web import RequestHandler

class WelcomeHandler(RequestHandler):

    def get(self):
        import django
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        self.write("Tornado Web Server with Django %s" % django.get_version())
        self.finish()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload',action='store_true',
                    dest='no_reload', default=False,
                    help='Tell Tornado not to auto-reload.'),
        )
    help = "Starts a single threaded Tornado web server."
    args = '[optional port number, or ipaddr:port]'

    def echo(self, *args, **kwargs):
        """Print in color to stdout"""
        text = " ".join([str(item) for item in args])
        if settings.DEBUG:
            color = kwargs.get("color",32)
            self.stdout.write("\033[0;%dm%s\033[0;m" % (color, text))
        else:
            self.stdout.write(text)

    def handle(self, addrport='', *args, **options):
        """Handle command call"""

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

        if args:
            raise CommandError('Usage is runserver %s' % self.args)
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
            raise CommandError("%r is not a valid port number." % port)

        self.quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
        self.run(*args, **options)

    def admin_media(self):
        """Return path and url of development admin media"""
        import django.contrib.admin as admin_media
        path = os.path.join(admin_media.__path__[0],'media')
        url = hasattr(settings,"ADMIN_MEDIA_PREFIX") and \
              settings.ADMIN_MEDIA_PREFIX or "/admin-media/"
        return (path, url,)

    def get_handler(self, *args, **kwargs):
        """Return Tornado application with Django WSGI handlers"""
        from django.core.handlers.wsgi import WSGIHandler
        from tornado import wsgi
        from tornado.web import Application, FallbackHandler, StaticFileHandler

        # Patch prepare method from Tornado's FallbackHandler
        from rjdj.djangotornado import patches
        FallbackHandler.prepare = patches.patch_prepare(FallbackHandler.prepare)

        django_app = wsgi.WSGIContainer(WSGIHandler())
        handlers = ()
        try:
            urls =  __import__(settings.ROOT_URLCONF,
                               fromlist=[settings.ROOT_URLCONF])
            if hasattr(urls,"tornado_urls"):
                handlers = urls.tornado_urls
        except ImportError:
            self.echo("No Tornado URL specified.",color=31)

        admin_media_path, admin_media_url = self.admin_media()
        handlers += (
            (r'/_', WelcomeHandler),
            (r'%s(.*)' % admin_media_url, StaticFileHandler, {"path": admin_media_path}),
            (r'.*', FallbackHandler, dict(fallback=django_app)),
            )
        return Application(handlers)

    def run(self, *args, **options):
        """Run application either with or without autoreload"""
        if options.get("no_reload",False):
            self.inner_run()
        else:
            from django.utils import autoreload
            autoreload.main(self.inner_run)

    def inner_run(self):
        """Get handler and start IOLoop"""
        import django
        from django.utils import translation
        from tornado import httpserver, ioloop

        self.echo("Validating models...\n")
        self.validate(display_num_errors=True)
        self.echo(("\nDjango version %(version)s, using settings %(settings)r\n"
                   "Server is running at http://%(addr)s:%(port)s/\n"
                   "Quit the server with %(quit_command)s.\n" ) % {
                      "version": django.get_version(),
                      "settings": settings.SETTINGS_MODULE,
                      "addr": self.addr,
                      "port": self.port,
                      "quit_command": self.quit_command,
                      })

        translation.activate(settings.LANGUAGE_CODE)

        app = self.get_handler()
        server = httpserver.HTTPServer(app)
        server.listen(int(self.port), address=self.addr)
        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            self.echo("\nShutting down Tornado ...\n",color=31)
            sys.exit(0)

