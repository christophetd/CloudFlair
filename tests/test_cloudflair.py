import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests

import cloudflair
from cloudflair import Cloudflair


class TestCloudflair(unittest.TestCase):
    @patch('cloudflair.censys_client')
    @patch('cloudflair.Cloudflare')
    def setUp(self, cloudflare_mock, censys_mock):
        self.cloudflair = Cloudflair("api_id", "api_secret")

    @patch('cloudflair.Cloudflare')
    @patch('cloudflair.dns_utils')
    def test_cloudflair_non_cloudflare_domain(self, dns_utils_mock, cloudflare_mock):
        # Scenario: a domain not behind Cloudflare is passed to Cloudflair
        dns_utils_mock.is_valid_domain.return_value = True
        cloudflare_mock.uses_cloudflare.return_value = False
        self.cloudflair.cloudflare = cloudflare_mock

        result = self.cloudflair.run("domain", "output file")

        self.assertEqual(set(), result)

    @patch('cloudflair.dns_utils')
    def test_cloudflair_invalid_domain(self, dns_utils_mock):
        # Scenario: an invalid domain is passed to Cloudflair
        dns_utils_mock.is_valid_domain.return_value = False
        with self.assertRaisesRegex(ValueError, "domain.+invalid"):
            hosts = self.cloudflair.find_hosts("somedomain")

    @patch('cloudflair.dns_utils')
    def test_cloudflair_find_hosts_no_certificates(self, dns_utils_mock):
        # Scenario: Censys doesn't return any certificate for the tested domain
        dns_utils_mock.is_valid_domain.return_value = True
        self.cloudflair.censys_client.get_certificates.return_value = []
        hosts = self.cloudflair.find_hosts("somedomain")
        self.assertEqual(set(), hosts)

    @patch('cloudflair.dns_utils')
    def test_cloudflair_find_hosts_no_hosts(self, dns_utils_mock):
        # Scenario: Censys returns certificates but no IP associated with them for the tested domain
        dns_utils_mock.is_valid_domain.return_value = True
        self.cloudflair.censys_client.get_certificates.return_value = ['fingerprint1', 'fingerprint2']
        self.cloudflair.censys_client.get_hosts.return_value = []

        hosts = self.cloudflair.find_hosts("somedomain")

        self.assertEqual(set(), hosts)

    @patch('cloudflair.Cloudflare')
    @patch('cloudflair.dns_utils')
    def test_cloudflair_find_hosts_filters_cloudflare_ips(self, dns_utils_mock, cloudflare_mock):
        # Ensure that Cloudflare IPs are filtered out from the origin IPs candidates
        # Here, we simulate the case where only Cloudflare IPs are returned
        dns_utils_mock.is_valid_domain.return_value = True
        cloudflare_mock.is_cloudflare_ip.return_value = False
        self.cloudflair.censys_client.get_certificates.return_value = ['fingerprint1', 'fingerprint2']
        self.cloudflair.censys_client.get_hosts.return_value = ['1.1.1.1', '2.2.2.2']

        hosts = self.cloudflair.find_hosts("somedomain")

        self.assertEqual(set(), hosts)

    @patch('cloudflair.Cloudflare')
    @patch('cloudflair.dns_utils')
    def test_cloudflair_find_hosts_with_cloudflare_hosts(self, dns_utils_mock, cloudflare_mock):
        # Ensure that Cloudflare IPs are filtered out from the origin IPs candidates
        # Here, we simulate the case where 1 Cloudflare IP and 1 non-Cloudflare IP are returned
        dns_utils_mock.is_valid_domain.return_value = True
        cloudflare_mock.is_cloudflare_ip.side_effect = lambda l: l == "1.1.1.1"
        self.cloudflair.censys_client.get_certificates.return_value = ['fingerprint1', 'fingerprint2']
        self.cloudflair.censys_client.get_hosts.return_value = ['1.1.1.1', '2.2.2.2']
        self.cloudflair.cloudflare = cloudflare_mock

        hosts = self.cloudflair.find_hosts("somedomain")

        self.assertSetEqual({"2.2.2.2"}, hosts)

    @patch('cloudflair.requests')
    def test_find_origins_original_page_non_200_status_code(self, requests_mock):
        # Scenario: the main domain's homepage returns a non-200 status code
        requests_mock.get.return_value = SimpleNamespace(url=None, status_code=403)
        with self.assertRaisesRegex(RuntimeError, "unexpected HTTP status code"):
            self.cloudflair.find_origins('domain', ['1.1.1.1'])

    @patch('cloudflair.requests')
    def test_find_origins_makes_correct_requests(self, requests_mock):
        # Ensures that correct requests are sent to origin candidates
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        requests_mock.get.return_value = mock_response

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        requests_mock.get.assert_called_once()
        args = requests_mock.get.call_args_list[0][1]
        self.assertEqual(args['url'], 'https://1.1.1.1')
        self.assertEqual(args['timeout'], cloudflair.config['http_timeout_seconds'])
        self.assertEqual(args['headers']['Host'], 'example.com')
        self.assertIn('User-Agent', args['headers'])

    @patch('cloudflair.requests')
    def test_find_origins_same_content(self, requests_mock):
        # Scenario: an origin candidate responds with exactly the same content as the main domain
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        requests_mock.get.return_value = mock_response

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        self.assertEqual(1, len(origins))
        self.assertEqual('1.1.1.1', origins[0][0])

    @patch('cloudflair.requests')
    def test_find_origins_similarity_below_threshold(self, requests_mock):
        # Scenario:  an origin candidate responds with a content "not similar enough" to the main domain
        cloudflair.similarity = Mock(return_value=cloudflair.config['response_similarity_threshold'] - 0.1)
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        mock_origin_response = SimpleNamespace(url='https://example.com', status_code=200, text='another text')
        requests_mock.get.return_value = mock_origin_response

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        self.assertEqual(0, len(origins))

    @patch('cloudflair.requests')
    def test_find_origins_similarity_above_threshold(self, requests_mock):
        # Scenario:  an origin candidate responds with a content "similar enough" to the main domain
        cloudflair.similarity = Mock(return_value=cloudflair.config['response_similarity_threshold'] + 0.1)
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        mock_origin_response = SimpleNamespace(url='https://example.com', status_code=200, text='another text')
        requests_mock.get.return_value = mock_origin_response

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        self.assertEqual(1, len(origins))
        self.assertEqual('1.1.1.1', origins[0][0])

    @patch('cloudflair.requests')
    def test_find_origins_non_200_status_code(self, requests_mock):
        # Scenario: one of the origins candidates responds with a non-200 status code
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        mock_candidate_response = SimpleNamespace(status_code=403, text='Unauthorized')
        requests_mock.get.return_value = mock_candidate_response

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        self.assertEqual(0, len(origins))

    def test_find_origins_timeout(self):
        # Scenario: one of the origins candidates times out
        #
        # Note: we can't mock the full requests package here, otherwise the tested code isn't able to catch
        # the requests-specific exception
        cloudflair.requests.get = Mock(side_effect=requests.exceptions.Timeout())
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)

        origins = self.cloudflair.find_origins('https://example.com', ['1.1.1.1'])

        self.assertEqual(0, len(origins))

    @patch('cloudflair.requests')
    def test_writes_origins_to_output_file(self, requests_mock):
        mock_response = SimpleNamespace(url='https://example.com', status_code=200, text='text')
        self.cloudflair.retrieve_original_page = Mock(return_value=mock_response)
        requests_mock.get.return_value = mock_response
        self.cloudflair.cloudflare.is_cloudflare_ip.return_value = False
        self.cloudflair.censys_client.get_certificates.return_value = ['fingerprint1']
        self.cloudflair.censys_client.get_hosts.return_value = ['1.1.1.1', '2.2.2.2']

        with tempfile.NamedTemporaryFile() as temp_file:
            self.cloudflair.run("example.com", temp_file.name)
            with open(temp_file.name, 'r') as f:
                self.assertSetEqual({"1.1.1.1", "2.2.2.2"}, set(f.read().splitlines()))
