import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock

import requests

import cloudflare


class TestCloudflare(unittest.TestCase):
    @patch('cloudflare.requests')
    def test_retrieves_ips(self, requests_mock):
        requests_mock.get.return_value = SimpleNamespace(status_code=200, text="1.1.1.1\n2.2.2.2")
        ips = cloudflare.Cloudflare().ip_ranges
        self.assertSetEqual({'1.1.1.1', '2.2.2.2'}, set(ips))

    @patch('cloudflare.requests')
    def test_returns_fallback_ip_ranges(self, requests_mock):
        requests_mock.get.side_effect = Mock(side_effect=requests.exceptions.RequestException)
        ips = cloudflare.Cloudflare().ip_ranges
        self.assertSetEqual(set(cloudflare.Cloudflare.default_ip_ranges), set(ips))

    @patch('cloudflare.requests')
    def test_cloudflare_ip(self, requests_mock):
        requests_mock.get.return_value = SimpleNamespace(status_code=200, text="1.1.1.1\n2.2.2.2")
        cl = cloudflare.Cloudflare()
        self.assertTrue(cl.is_cloudflare_ip("1.1.1.1"))
        self.assertFalse(cl.is_cloudflare_ip("3.3.3.3"))

    @patch('cloudflare.requests')
    @patch('cloudflare.dns')
    def test_is_cloudflare_domain(self, dns_mock, requests_mock):
        requests_mock.get.return_value = SimpleNamespace(status_code=200, text="1.1.1.1\n2.2.2.2")
        cl = cloudflare.Cloudflare()

        dns_mock.resolver.query.return_value = ['1.1.1.1']
        self.assertTrue(cl.uses_cloudflare("example.com"))

        dns_mock.resolver.query.return_value = ['3.3.3.3']
        self.assertFalse(cl.uses_cloudflare("example.com"))

        dns_mock.resolver.query.return_value = ['3.3.3.3', '1.1.1.1']
        self.assertTrue(cl.uses_cloudflare("example.com"))
