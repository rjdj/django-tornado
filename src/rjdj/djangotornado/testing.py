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

import urllib2
import urllib
import threading

from tornado import ioloop, httpserver
from tornado.httpclient import HTTPClient, HTTPRequest
from tornado.web import Application, RequestHandler

from rjdj.djangotornado.signals import tornado_exit
from rjdj.djangotornado.utils import get_named_urlspecs

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from rjdj.djangotornado.shortcuts import set_application

class TestResponse(object):
    """Wrapper for urllib repsonse"""

    def __init__(self, status_code=200, content="", headers={}):
        self.status_code = status_code
        self.content = content
        self._headers = TestResponseHeaders(headers)

    def raw_response(self):
        raw_response = ""
        for key,value in self._headers.__dict__.iteritems():
            raw_response += "%s: %s\n" % (key.capitalize(),value)
        raw_response += self.content
        return raw_response

    __str__ = __repr__ = raw_response


class TestResponseHeaders:
    """Header representation for the TestResponse"""

    def __init__(self, header_dict):
        for k,v in header_dict.iteritems():
            setattr(self, k, v)

    def __setitem__(self, key, value):
        raise AttributeError("You are not allowed to set headers once they are defined.")

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return str(sorted(self.__dict__.iteritems(), key=lambda x: x[0]))


class TestResponseHandler(urllib2.BaseHandler):
    """Custom handler for 400's and 500's responses"""

    def general_response(self, req, page, code, msg, hdrs):
        return page

    http_error_400 = http_error_404 = http_error_405 = http_error_500 = general_response



class TestServer(httpserver.HTTPServer):
    """Test Server for Tornado"""

    port = 10000
    address = "localhost"
    _io_thread = None
    _started = False

    def __init__(self, handlers, io_loop=None):

        application = Application(get_named_urlspecs(handlers))
        io_loop = io_loop or ioloop.IOLoop.instance()
        super(TestServer, self).__init__(application, io_loop=io_loop)
        set_application(application)


    def start(self):
        raise Exception("""You are not allowed to spawn a test server
in the same thread as the test.

Use 'testserver.run()' instead!
""")

    def run(self):
        """Start in background"""
        assert not self._sockets
        if not self._started:
            if not self.io_loop.running():
                self._io_thread = threading.Thread(target=self._run_background)
                self._io_thread.daemon = True
                self._io_thread.start()
            self.bind(self.port, address=self.address)
            super(TestServer, self).start()
            self._started = True
        else:
            print "Nothing to do. Server already started."

    def _run_background(self):
        self.io_loop.start()

    def update_app(self, handlers):
        """Stop server, update handlers, and start in backgrounda again"""
        self._stop()
        self.request_callback = Application(handlers)
        self.run()

    def _stop(self):
        if self._started:
            self.io_loop.stop()
            self._io_thread.join()
            self._io_thread = None
            self.stop()
            self._sockets = {}
            self._started = False
            
            # send exit signal
            tornado_exit.send_robust(sender = self)

    def __del__(self):
        print "Kill IOLoop thread: %s " % self._io_thread
        print "Kill current thread: %s" % threading.current_thread()
        self._stop()



class TestClient(object):
    """Test Client for Tornado"""

    _server = None

    def __init__(self, handlers, io_loop=None):
        self._server = TestServer(handlers, io_loop)

    def get_url(self, uri, protocol="http"):
        if not (type(protocol) == str or type(protocol) == unicode):
            raise TypeError("Protocol must be string or unicode.")
        return str("%s://%s:%d%s" % (
            protocol,
            self._server.address,
            self._server.port,
            uri))

    def fetch(self, method, uri, data=None, files = {}, **options):
        protocol = options.get("protocol","http")
        headers = {}
        opener = None
        if data:
            if method == "GET":
                # add GET parameters to url and force data to be None
                uri += "?%s" % urllib.urlencode(data)
                data = None
            elif method == "POST":
                # urlencode POST parameters
                if files:
                    opener = register_openers()
                    data.update(files)
                    data, headers = multipart_encode(data)
                else:            
                    data = urllib.urlencode(data)
                    
        else:
            if method == "POST":
                # force POST even without POST data
                data = urllib.urlencode({})


        opener = opener or urllib2.build_opener()
        opener.add_handler(TestResponseHandler())
        try:
            self._server.run()
            response = opener.open(urllib2.Request(self.get_url(uri,protocol), data, headers))
            content = response.read()
        except: raise
        finally:
            self._server._stop()
        return TestResponse(response.code, content, response.headers.dict)

    def get(self, uri, data=None, **options):
        return self.fetch("GET", uri, data, **options)

    def post(self, uri, data=None, files = {}, **options):
        return self.fetch("POST", uri, data, files, **options)

    def put(self, uri, data=None, **options):
        raise NotImplementedError

    def delete(self, uri, data=None, **options):
        raise NotImplementedError

    def __del__(self):
        if self._server:
            self._server.__del__()
