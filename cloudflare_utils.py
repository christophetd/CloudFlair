#!/usr/bin/env python3

import ipaddress
from dns import resolver
import sys

#  TODO: fetch it from https://www.cloudflare.com/ips-v4 instead
cloudflare_ip_ranges = [
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

if sys.version_info[0] == 2:
    cloudflare_subnets = [ ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in cloudflare_ip_ranges ]
else:
    cloudflare_subnets = [ ipaddress.ip_network(ip_range) for ip_range in cloudflare_ip_ranges ]

def is_cloudflare_ip(ip):
    for cloudflare_subnet in cloudflare_subnets:
        if cloudflare_subnet.overlaps(ipaddress.ip_network(ip)):
            return True
    return False

def uses_cloudflare(domain):
    answers = resolver.query(domain, 'A')

    for answer in answers:
        if is_cloudflare_ip(answer):
            return True

    return False
