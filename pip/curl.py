from pip.shell import ShellClient


class RequestException(Exception):
    pass


class RequestFailed(RequestException):

    def __init__(self, msg, method, url):
        self._msg = "Failed to %s %s. %s" % (method, url, msg)
        super(RequestFailed, self).__init__(self._msg)


class ResponseFailed(RequestException):

    def __init__(self, response):
        self._msg = "Failed to %s. Response: %s" % (response, response.content)
        super(ResponseFailed, self).__init__(self._msg)
        self.response = response


class CurlResponse(object):

    def __init__(self, output, method, url):
        self._output = output
        self.method = method
        self.url = url

    @property
    def _data(self):
        parts = self._output.split('\r\n\r\n')
        content = parts.pop()
        header_lines = parts.pop().split('\r\n')
        status = int(header_lines.pop(0).split()[-1])
        header = dict([[i.strip() for i in l.split(':', 1)]
                       for l in header_lines])
        return dict(status=status, header=header, content=content)

    def __str__(self):
        return "%s %s (status: %s)" % (self.method, self.url, self.status)

    def __repr__(self):
        return "<CurlResponse %s>" % self

    @property
    def ok(self):
        return self.status == 200

    @property
    def status(self):
        return self._data['status']

    @property
    def header(self):
        return self._data['header']

    @property
    def content(self):
        return self._data['content']


class Curl(object):

    def __init__(self, shell=None):
        self.shell = shell or ShellClient()

    def get(self, url):
        output = self.shell.run('curl -iL %s' % url)
        response = CurlResponse(output, 'get', url)
        if not response.ok:
            raise ResponseFailed(response)
        return response
