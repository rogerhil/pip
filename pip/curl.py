from json import dumps
try:
    from urllib.parse import urlencode  # pylint: disable=E0611,F0401
except ImportError:
    from urllib import urlencode

from pip.shell import ShellClient, CommandFailed


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
        parts = self._output.split(b'\r\n\r\n')
        content = parts.pop()
        header_lines = parts.pop().split(b'\r\n')
        status = int(header_lines.pop(0).split()[-1])
        header = dict([[i.strip() for i in l.split(b':', 1)]
                       for l in header_lines])
        return dict(status=status, headers=header, content=content)

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
    def headers(self):
        return self._data['headers']

    @property
    def content(self):
        return self._data['content']


class Curl(object):

    base_cmd = "curl -iL -X %s"

    def __init__(self, shell=None):
        self.shell = shell or ShellClient()

    def request(self, method, url, params=None, data=None, json=None,
                headers=None, user=None, password=None,
                timeout=None, insecure=False, head_only=False):
        headers = headers or {}
        data = data or {}
        json = json or {}
        headers_str = ''
        user_str = ''
        content_type = ''
        data_str = ''
        timeout_str = ''
        if timeout:
            timeout_str = ' -m %s' % timeout
        if params:
            url = '%s?%s' % (url, urlencode(params))
        if data:
            content_type = 'application/x-www-form-urlencoded'
            if isinstance(data, dict):
                data = urlencode(data)
            data_str = ' -d "%s"' % data.replace('\\', '\\\\').replace('"', '\\"')
        elif json:
            content_type = 'application/json'
            data_str = " -d '%s'" % dumps(json)
        if content_type and 'Content-Type' not in headers:
            headers['Content-Type'] = content_type
        if headers:
            headers_str = " %s" % ' '.join(['-H "%s: %s"' % (k, v)
                                            for k, v in headers.items()])
        if user and password:
            user_str = " -u %s:%s" % (user, password)
        head = " --head" if head_only else ""
        insecure = " --insecure" if insecure else ""
        cmd = '%s%s%s%s%s%s%s "%s"' % (self.base_cmd % method.upper(),
                                       user_str, headers_str, data_str,
                                       timeout_str, insecure, head, url)
        try:
            output = self.shell.run(cmd)
        except CommandFailed as err:
            msg = "Curl command failed on %s: %s. Output: %s" % \
                  (self.shell.host, cmd, str(err))
            raise RequestFailed(msg, method, url)
        response = CurlResponse(output, method, url)
        if not response.ok:
            raise ResponseFailed(response)
        return response

    def get(self, url, params=None, headers=None, user=None, password=None,
            timeout=None, insecure=False, head_only=False):
        return self.request('get', url, params, headers=headers, user=user,
                            password=password, timeout=timeout,
                            insecure=insecure, head_only=head_only)

    def post(self, url, params=None, data=None, json=None, headers=None,
             user=None, password=None, timeout=None):
        return self.request('post', url, params=params, data=data, json=json,
                            headers=headers, user=user, password=password,
                            timeout=timeout)

    def put(self, url, params=None, data=None, json=None, headers=None,
            user=None, password=None, timeout=None):
        return self.request('put', url, params=params, data=data, json=json,
                            headers=headers, user=user, password=password,
                            timeout=timeout)

    def delete(self, url, header=None, user=None, password=None,
               timeout=None):
        return self.request('delete', url, headers=header, timeout=timeout,
                            user=user, password=password)
