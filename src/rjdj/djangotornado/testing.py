##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# All Rights Reserved.
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

class TestResponse(object):
    """Wrapper for urllib repsonse"""

    def __init__(self, status_code=200, content="", headers={}):
        self.status_code = status_code
        self.content = content
        self._headers = TestResponseHeaders(headers)

    def raw_response(self):
        raw_response = ""
        for key,value in self._headers.__dict__.items():
            raw_response += "%s: %s\n" % (key.capitalize(),value)
        raw_response += self.content
        return raw_response

    __str__ = __repr__ = raw_response


class TestResponseHeaders:
    """Header representation for the TestResponse"""

    def __init__(self, header_dict):
        for k,v in header_dict.items():
            setattr(self, k, v)

    def __setitem__(self, key, value):
        raise AttributeError("You are not allowed to set headers once they are defined.")

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return str(sorted(self.__dict__.items(), key=lambda x: x[0]))


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
        application = Application(handlers)
        io_loop = io_loop or ioloop.IOLoop.instance()
        super(TestServer, self).__init__(application, io_loop=io_loop)

    def start(self):
        raise Exception("""You are not allowed to spawn a test server
in the same thread as the test.

Use 'testserver.run()' instead!
""")

    def run(self):
        """Start in background"""
        assert not self._socket
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

    def try_bind(self, port):
        if port > 11000:
            raise Exception("Max ports reached.")
        try:
            self.bind(port) #, "localhost")
        except Exception, e:
            import pdb; pdb.set_trace()
            print "Try to bind port %d ... failed" % port
            port += 1
            print "New port %d" % port
            self.try_bind(port)
        return port

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
            del self._socket
            self._socket = None
            self._started = False

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

    def fetch(self, method, uri, data=None, **options):
        protocol = options.get("protocol","http")

        if data:
            if method == "GET":
                # add GET parameters to url and force data to be None
                uri += "?%s" % urllib.urlencode(data)
                data = None
            elif method == "POST":
                # urlencode POST parameters
                data = urllib.urlencode(data)
        else:
            if method == "POST":
                # force POST even without POST data
                data = urllib.urlencode({})

        self._server.run()
        opener = urllib2.build_opener()
        opener.add_handler(TestResponseHandler())
        response = opener.open(self.get_url(uri,protocol), data)
        content = response.read()
        self._server._stop()
        return TestResponse(response.code, content, response.headers.dict)

    def get(self, uri, data=None, **options):
        return self.fetch("GET", uri, data, **options)

    def post(self, uri, data=None, **options):
        return self.fetch("POST", uri, data, **options)

    def put(self, uri, data=None, **options):
        raise NotImplementedError

    def delete(self, uri, data=None, **options):
        raise NotImplementedError

    def __del__(self):
        if self._server:
            self._server.__del__()
