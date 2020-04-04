import sys

import dns
import ipaddress
import requests


class Cloudflare:
    default_ip_ranges = [
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "104.16.0.0/12",
        "108.162.192.0/18",
        "131.0.72.0/22",
        "141.101.64.0/18",
        "162.158.0.0/15",
        "172.64.0.0/13",
        "173.245.48.0/20",
        "188.114.96.0/20",
        "190.93.240.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17"
    ]

    def __init__(self):
        self.ip_ranges = self._fetch_ip_ranges()
        self.subnets = self._build_subnets()

    def _fetch_ip_ranges(self):
        url = 'https://www.cloudflare.com/ips-v4'
        try:
            print('[*] Retrieving Cloudflare IP ranges from {}'.format(url))
            page_content = requests.get(url, timeout=10)
            ip_ranges_text = page_content.text
            return [ip for ip in ip_ranges_text.split("\n") if ip]

        except IOError:
            sys.stderr.write('[-] Failed to retrieve Cloudflare IP ranges - using a default (possibly outdated) list\n')
            return Cloudflare.default_ip_ranges

    def _build_subnets(self):
        if sys.version_info[0] == 2:
            return [ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in self.ip_ranges]
        else:
            return [ipaddress.ip_network(ip_range) for ip_range in self.ip_ranges]

    def is_cloudflare_ip(self, ip):
        for cloudflare_subnet in self.subnets:
            if cloudflare_subnet.overlaps(ipaddress.ip_network(ip)):
                return True
        return False

    def uses_cloudflare(self, domain):
        answers = dns.resolver.query(domain, 'A')
        for answer in answers:
            if self.is_cloudflare_ip(answer):
                return True
        return False


"""

# Removes any Cloudflare IPs from the given list
def filter_cloudflare_ips(ips):
    return [ip for ip in ips if not is_cloudflare_ip(ip)]
"""
