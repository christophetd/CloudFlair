import censys
import censys.certificates
import censys.ipv4


class CensysClient:
    def __init__(self, api_id, api_secret):
        self.api_id = api_id
        self.api_secret = api_secret
        self.censys_certificates = censys.certificates.CensysCertificates(
            api_id=self.api_id,
            api_secret=self.api_secret
        )
        self.censys_hosts = censys.ipv4.CensysIPv4(
            api_id=self.api_id,
            api_secret=self.api_secret
        )

    def get_certificates(self, domain):
        try:
            requested_fields = [
                'parsed.names',
                'parsed.fingerprint_sha256'
            ]
            certificate_query = 'parsed.names: %s AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com' % domain
            certificates_search_results = self.censys_certificates.search(certificate_query, fields=requested_fields)
            return set([cert['parsed.fingerprint_sha256'] for cert in certificates_search_results])
        except censys.base.CensysUnauthorizedException:
            raise RuntimeError('Your Censys credentials look invalid.')
        except censys.base.CensysRateLimitExceededException:
            raise RuntimeError('Looks like you exceeded your Censys account limits rate. Exiting')

    def get_hosts(self, cert_fingerprints):
        try:
            hosts_query = ' OR '.join(cert_fingerprints)
            hosts_search_results = self.censys_hosts.search(hosts_query)
            return set([host_search_result['ip'] for host_search_result in hosts_search_results])
        except censys.base.CensysUnauthorizedException:
            raise RuntimeError('Your Censys credentials look invalid.\n')
        except censys.base.CensysRateLimitExceededException:
            raise RuntimeError('Looks like you exceeded your Censys account limits rate. Exiting')
