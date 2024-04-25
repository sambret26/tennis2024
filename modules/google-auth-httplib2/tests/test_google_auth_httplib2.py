# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib2
import mock
import six
from six.moves import http_client

import google_auth_httplib2
from tests import compliance


class MockHttp(object):
    def __init__(self, responses, headers=None):
        self.responses = responses
        self.requests = []
        self.headers = headers or {}

    def request(self, url, method='GET', body=None, headers=None, **kwargs):
        self.requests.append((method, url, body, headers, kwargs))
        return self.responses.pop(0)


class MockResponse(object):
    def __init__(self, status=http_client.OK, data=b''):
        self.status = status
        self.data = data

    def __iter__(self):
        yield self
        yield self.data


class TestRequestResponse(compliance.RequestResponseTests):
    def make_request(self):
        http = httplib2.Http()
        return google_auth_httplib2.Request(http)

    def test_timeout(self):
        url = 'http://example.com'
        http = MockHttp(responses=[MockResponse()])
        request = google_auth_httplib2.Request(http)
        request(url=url, method='GET', timeout=5)

        assert http.requests[0] == (
            'GET', url, None, None, {})


def test__make_default_http():
    http = google_auth_httplib2._make_default_http()
    assert isinstance(http, httplib2.Http)


class MockCredentials(object):
    def __init__(self, token='token'):
        self.token = token

    def apply(self, headers):
        headers['authorization'] = self.token

    def before_request(self, request, method, url, headers):
        self.apply(headers)

    def refresh(self, request):
        self.token += '1'


class TestAuthorizedHttp(object):
    TEST_URL = 'http://example.com'

    def test_authed_http_defaults(self):
        authed_http = google_auth_httplib2.AuthorizedHttp(
            mock.sentinel.credentials)

        assert authed_http.credentials == mock.sentinel.credentials
        assert isinstance(authed_http.http, httplib2.Http)

    def test_connections(self):
        authed_http = google_auth_httplib2.AuthorizedHttp(
            mock.sentinel.credentials)

        assert authed_http.connections == authed_http.http.connections

        authed_http.connections = mock.sentinel.connections
        assert authed_http.http.connections == mock.sentinel.connections

    def test_request_no_refresh(self):
        mock_credentials = mock.Mock(wraps=MockCredentials())
        mock_response = MockResponse()
        mock_http = MockHttp([mock_response])

        authed_http = google_auth_httplib2.AuthorizedHttp(
            mock_credentials, http=mock_http)

        response, data = authed_http.request(self.TEST_URL)

        assert response == mock_response
        assert data == mock_response.data
        assert mock_credentials.before_request.called
        assert not mock_credentials.refresh.called
        assert mock_http.requests == [
            ('GET', self.TEST_URL, None, {'authorization': 'token'}, {})]

    def test_request_refresh(self):
        mock_credentials = mock.Mock(wraps=MockCredentials())
        mock_final_response = MockResponse(status=http_client.OK)
        # First request will 401, second request will succeed.
        mock_http = MockHttp([
            MockResponse(status=http_client.UNAUTHORIZED),
            mock_final_response])

        authed_http = google_auth_httplib2.AuthorizedHttp(
            mock_credentials, http=mock_http)

        response, data = authed_http.request(self.TEST_URL)

        assert response == mock_final_response
        assert data == mock_final_response.data
        assert mock_credentials.before_request.call_count == 2
        assert mock_credentials.refresh.called
        assert mock_http.requests == [
            ('GET', self.TEST_URL, None, {'authorization': 'token'}, {}),
            ('GET', self.TEST_URL, None, {'authorization': 'token1'}, {})]

    def test_request_stream_body(self):
        mock_credentials = mock.Mock(wraps=MockCredentials())
        mock_response = MockResponse()
        # Refresh is needed to cover the resetting of the body position.
        mock_http = MockHttp([
            MockResponse(status=http_client.UNAUTHORIZED),
            mock_response])

        body = six.StringIO('body')
        body.seek(1)

        authed_http = google_auth_httplib2.AuthorizedHttp(
            mock_credentials, http=mock_http)

        response, data = authed_http.request(
            self.TEST_URL, method='POST', body=body)

        assert response == mock_response
        assert data == mock_response.data
        assert mock_http.requests == [
            ('POST', self.TEST_URL, body, {'authorization': 'token'}, {}),
            ('POST', self.TEST_URL, body, {'authorization': 'token1'}, {})]
