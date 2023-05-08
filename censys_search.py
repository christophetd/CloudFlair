import sys

from censys.common.exceptions import (
    CensysRateLimitExceededException,
    CensysUnauthorizedException,
)
from censys.search import CensysCerts, CensysHosts

USER_AGENT = (
    f"{CensysCerts.DEFAULT_USER_AGENT} (CloudFlair; +https://github.com/christophetd/CloudFlair)"
)
INVALID_CREDS = "[-] Your Censys credentials look invalid.\n"
RATE_LIMIT = "[-] Looks like you exceeded your Censys account limits rate. Exiting\n"


def get_certificates(domain, api_id, api_secret, pages=2) -> set:
    try:
        censys_certificates = CensysCerts(
            api_id=api_id, api_secret=api_secret, user_agent=USER_AGENT
        )

        certificate_query = f"names: {domain} and parsed.signature.valid: true and not names: cloudflaressl.com"
        certificates_search_results = censys_certificates.search(
            certificate_query, per_page=100, pages=pages
        )

        fingerprints = set()
        for page in certificates_search_results:
            for cert in page:
                fingerprints.add(cert["fingerprint_sha256"])
        return fingerprints
    except CensysUnauthorizedException:
        sys.stderr.write(INVALID_CREDS)
        exit(1)
    except CensysRateLimitExceededException:
        sys.stderr.write(RATE_LIMIT)
        exit(1)


def get_hosts(cert_fingerprints, api_id, api_secret):
    try:
        censys_hosts = CensysHosts(
            api_id=api_id, api_secret=api_secret, user_agent=USER_AGENT
        )
        hosts_query = f"services.tls.certificates.leaf_data.fingerprint: {{{','.join(cert_fingerprints)}}}"
        hosts_search_results = censys_hosts.search(hosts_query).view_all()
        return set(
            [r["ip"] for r in hosts_search_results.values()]
        )
    except CensysUnauthorizedException:
        sys.stderr.write(INVALID_CREDS)
        exit(1)
    except CensysRateLimitExceededException:
        sys.stderr.write(RATE_LIMIT)
        exit(1)
