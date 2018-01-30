#!/usr/bin/env python3

import dns
import ipaddress
import sys

import requests


def get_cloudflare_ip_ranges():
    cloudflare_ip_ranges_url = 'https://www.cloudflare.com/ips-v4'
    try:
        page_content = requests.get(cloudflare_ip_ranges_url, timeout=10)
        ip_ranges_text = page_content.text
        return [ip for ip in ip_ranges_text.split("\n") if ip]
    except requests.exceptions.RequestException:
        pass


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
