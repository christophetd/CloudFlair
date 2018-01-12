#!/usr/bin/env python3

import censys.certificates
import censys.ipv4
import censys
import sys

def get_certificates(domain, api_id, api_secret):
    try:
        censys_certificates = censys.certificates.CensysCertificates(api_id=api_id, api_secret=api_secret)

        requested_fields = [
            'parsed.names',
            'parsed.fingerprint_sha256'
        ]

        certificate_query = 'parsed.names: %s AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com' % domain
        certificates_search_results = censys_certificates.search(certificate_query, fields=requested_fields)
        return set([ cert['parsed.fingerprint_sha256'] for cert in certificates_search_results ])
    except censys.base.CensysUnauthorizedException:
        sys.stderr.write('[-] Your Censys credentials look invalid.\n')
        exit(1)
    except censys.base.CensysRateLimitExceededException:
        sys.stderr.write('[-] Looks like you exceeded your Censys account limits rate. Exiting\n')
        exit(1)

def get_hosts(cert_fingerprints, api_id, api_secret):
    try:
        censys_hosts = censys.ipv4.CensysIPv4(api_id=api_id, api_secret=api_secret)
        hosts_query = ' OR '.join(cert_fingerprints)

        hosts_search_results = censys_hosts.search(hosts_query)
        return set([ host_search_result['ip'] for host_search_result in hosts_search_results ])
    except censys.base.CensysUnauthorizedException:
        sys.stderr.write('[-] Your Censys credentials look invalid.\n')
        exit(1)
    except censys.base.CensysRateLimitExceededException:
        sys.stderr.write('[-] Looks like you exceeded your Censys account limits rate. Exiting\n')
        exit(1)