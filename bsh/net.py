import requests


class Net(object):

    def request(self, method, url, headers=None, params=None, data=None, **kwargs):
        _headers = {'user-agent': 'wasp', 'referer': url}

        if headers is None:
            headers = _headers

        if 'user-agent' not in headers:
            headers.update({'user-agent': 'wasp'})

        return requests.request(method, url, headers=headers, params=params, data=data, **kwargs)

    def get(self, url, headers=None, params=None, **kwargs):
        return self.request('GET', url, headers=headers, params=params, data=None, **kwargs)

    def post(self, url, headers=None, data=None, **kwargs):
        return self.request('POST', url, headers=headers, params=None, data=data, **kwargs)
