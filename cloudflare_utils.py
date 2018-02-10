import dns
import ipaddress
import sys

import requests


def get_cloudflare_ip_ranges():
    cloudflare_ip_ranges_url = 'https://www.cloudflare.com/ips-v4'
    ip_ranges = []
    ip_ranges_fallback = [
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

    try:
        print('[*] Retrieving Cloudflare IP ranges from {}'.format(cloudflare_ip_ranges_url))
        page_content = requests.get(cloudflare_ip_ranges_url, timeout=10)
        ip_ranges_text = page_content.text
        ip_ranges = [ip for ip in ip_ranges_text.split("\n") if ip]

    except requests.exceptions.RequestException:
        sys.stderr.write('[-] Failed to retrieve Cloudflare IP ranges - using a default (possibly outdated) list\n')
        ip_ranges = ip_ranges_fallback

    finally:
        return ip_ranges


cloudflare_ip_ranges = get_cloudflare_ip_ranges()

if sys.version_info[0] == 2:
    cloudflare_subnets = [ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in cloudflare_ip_ranges]
else:
    cloudflare_subnets = [ipaddress.ip_network(ip_range) for ip_range in cloudflare_ip_ranges]


def is_cloudflare_ip(ip):
    for cloudflare_subnet in cloudflare_subnets:
        if cloudflare_subnet.overlaps(ipaddress.ip_network(ip)):
            return True
    return False


def uses_cloudflare(domain):
    answers = dns.resolver.query(domain, 'A')

    for answer in answers:
        if is_cloudflare_ip(answer):
            return True

    return False
