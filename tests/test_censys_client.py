import unittest
from unittest.mock import patch, Mock

from censys_client import CensysClient


class TestCensysClient(unittest.TestCase):
    @patch('censys_client.censys.ipv4')
    @patch('censys_client.censys.certificates')
    def setUp(self, censys_certificates_mock, censys_ipv4_mock):
        censys_certificates_mock.CensysCertificates = Mock()
        censys_ipv4_mock.CensysIPv4 = Mock()
        self.client = CensysClient("id", "secret")

    def test_certificates(self):
        self.client.censys_certificates.search.return_value = [
            {'parsed.fingerprint_sha256': 'a'},
            {'parsed.fingerprint_sha256': 'b'},
            {'parsed.fingerprint_sha256': 'c'}
        ]
        certificates = self.client.get_certificates("domain.tld")
        self.assertSetEqual({'a', 'b', 'c'}, set(certificates))

    def test_hosts(self):
        self.client.censys_hosts.search.return_value = [
            {'host': 'a', 'ip': '1.1.1.1'},
            {'host': 'b', 'ip': '2.2.2.2'},
            {'host': 'c', 'ip': '3.3.3.3'}
        ]
        hosts = self.client.get_hosts(["dontcare"])
        self.assertSetEqual({'1.1.1.1', '2.2.2.2', '3.3.3.3'}, hosts)
