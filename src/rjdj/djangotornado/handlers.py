##############################################################################
#
# Copyright (c) 2011 Reality Jockey Ltd. and Contributors.
# All Rights Reserved.
#
##############################################################################

# -*- coding: utf-8 -*-

__docformat__ = "reStructuredText"

from threading import Thread
from tornado.web import RequestHandler, asynchronous
from django.http import HttpRequest, QueryDict , MultiValueDict


class DjangoRequest(HttpRequest):
    """Tornado Request --> Django Request"""

    _tornado_request = None

    def __init__(self, tornado_request_type):
        self._tornado_request = tornado_request_type
        super(DjangoRequest,self).__init__()
        self.tornado_to_django()

    def tornado_to_django(self):
        tr = self._tornado_request

        if not tr.method:
            raise KeyError("Missing method in request")
        if tr.method not in ["GET","POST"]:
            raise ValueError("Method must be GET or POST")

        self.method = tr.method
        self.path = tr.uri
        self.path_info = ''

        self.GET = QueryDict(self.raw_get_data, encoding=self._encoding)
        self.POST = QueryDict(self.raw_post_data, encoding=self._encoding)
        self.FILES = MultiValueDict({})

        self.META["SERVER_NAME"] = tr.host
        self.META["HTTP_HOST"] = tr.host
        self.META["PROTOCOL"] = tr.protocol
        self.META["REMOTE_ADDR"] = tr.remote_ip
        #self.META["SERVER_PORT"] = 8000
        if hasattr(tr,"cookies"):
            for k,v in tr.cookies:
                self.COOKIES[k] = v

        self.user = None
        self.session = {}

    def build_absolute_uri(self,location=None):
        uri = super(DjangoRequest,self).build_absolute_uri(location)
        return unicode(uri)

    def __setitem__(self, key, value):
        if hasattr(self,key):
            setattr(self,key,value)
        else:
            self.META[key] = value

    @property
    def raw_get_data(self):
        return self._tornado_request.query

    @property
    def raw_post_data(self):
        return self._tornado_request.body


class DjangoHandler(RequestHandler):
    """Handler for Django views"""

    django_view = None

    def __init__(self, application, request, **kwargs):
        if "django_view" in kwargs.keys():
            self.django_view = kwargs.get("django_view")
        else:
            raise KeyError("Missing key 'django_view' in keyword arguments.")
        super(DjangoHandler,self).__init__(application, request)

    def convert_response(self, response):
        self.set_status(response.status_code)
        for k,v in response.items():
            self.set_header(k, v)
        if hasattr(response, "render"):
            response.render()
        self.write(response.content)

    def start_thread(self, request, *args):
        request = DjangoRequest(request)
        thread = Thread(target = self.worker,
                        args = (request,) + args,
                        kwargs = {})
        thread.daemon = True
        thread.start()

    def worker(self, *args):
        """Worker that is processes in separate thread"""
        res = self.django_view(*args)
        cb = self.async_callback(self.return_response, res)
        _io_loop.add_callback(cb)

    @asynchronous
    def get(self, *args):
        """GET Handler"""
        self.start_thread(self.request, *args)

    @asynchronous
    def post(self, *args):
        """POST Handler"""
        self.start_thread(self.request, *args)

    def return_response(self, response):
        try:
            self.convert_response(response)
        finally:
            self.finish()
