import sys

from censys.common import __version__
from censys.common.exceptions import (
    CensysRateLimitExceededException,
    CensysUnauthorizedException,
)
from censys.search import CensysCertificates, CensysIPv4

USER_AGENT = (
    f"censys/{__version__} (CloudFlair; +https://github.com/christophetd/CloudFlair)"
)
INVALID_CREDS = "[-] Your Censys credentials look invalid.\n"
RATE_LIMIT = "[-] Looks like you exceeded your Censys account limits rate. Exiting\n"


def get_certificates(domain, api_id, api_secret):
    try:
        censys_certificates = CensysCertificates(
            api_id=api_id, api_secret=api_secret, user_agent=USER_AGENT
        )

        requested_fields = ["parsed.names", "parsed.fingerprint_sha256"]

        certificate_query = f"parsed.names: {domain} AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com"
        certificates_search_results = censys_certificates.search(
            certificate_query, fields=requested_fields
        )
        return set(
            [cert["parsed.fingerprint_sha256"] for cert in certificates_search_results]
        )
    except CensysUnauthorizedException:
        sys.stderr.write(INVALID_CREDS)
        exit(1)
    except CensysRateLimitExceededException:
        sys.stderr.write(RATE_LIMIT)
        exit(1)


def get_hosts(cert_fingerprints, api_id, api_secret):
    try:
        censys_hosts = CensysIPv4(
            api_id=api_id, api_secret=api_secret, user_agent=USER_AGENT
        )
        hosts_query = " OR ".join(cert_fingerprints)

        hosts_search_results = censys_hosts.search(hosts_query)
        return set(
            [host_search_result["ip"] for host_search_result in hosts_search_results]
        )
    except CensysUnauthorizedException:
        sys.stderr.write(INVALID_CREDS)
        exit(1)
    except CensysRateLimitExceededException:
        sys.stderr.write(RATE_LIMIT)
        exit(1)
