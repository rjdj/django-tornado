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

def color_print(*args, **kwargs):
    text = " ".join([str(item) for item in args])
    if settings.DEBUG:
        color = kwargs.get("color",32)
        print "\033[0;%dm%s\033[0;m" % (color, text)
    else:
        print text

class TestHandler(RequestHandler):

    def get(self):
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        self.write("Welcome to Tornado Web Server!")
        self.finish()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload',action='store_true',
                    dest='no_reload', default=False,
                    help='Tell Tornado not to auto-reload.'),
        )
    help = "Starts a single threaded Tornado web server."
    args = '[optional port number, or ipaddr:port]'

    def handle(self, addrport='', *args, **options):
        import django
        from django.core.handlers.wsgi import WSGIHandler
        from tornado import httpserver, wsgi, ioloop
        from tornado.web import Application, FallbackHandler

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)


        if args:
            raise CommandError('Usage is runserver %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'

        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)

        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        def inner_run():
            color_print("Validating models...")
            self.validate(display_num_errors=True)
            color_print("\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE))
            color_print("Server is running at http://%s:%s/" % (addr,port))
            color_print("Quit the server with %s." % quit_command)

            django_app = wsgi.WSGIContainer(WSGIHandler())
            tornado_app = Application([
                (r'/_t/', TestHandler),
                (r'.*', FallbackHandler, dict(fallback=django_app)),
                ])
            server = httpserver.HTTPServer(tornado_app)
            server.listen(int(port), address=addr)
            try:
                ioloop.IOLoop.instance().start()
            except KeyboardInterrupt:
                color_print("\nShutting down Tornado ...",color=31)
                sys.exit(0)

        if options.get("no_reload",False):
            inner_run()
        else:
            from django.utils import autoreload
            autoreload.main(inner_run)
