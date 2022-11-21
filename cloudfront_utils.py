import dns
import ipaddress
import json
import sys

import requests


def get_cloudfront_ip_ranges():
    cloudfront_ip_ranges_url = 'https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips'
    cloudfront_backup_ip_ranges_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
    ip_ranges = []

    try:
        print('[*] Retrieving Cloudfront IP ranges from {}'.format(cloudfront_ip_ranges_url))
        page_content = requests.get(cloudfront_ip_ranges_url, timeout=10)
        ip_ranges_json = json.loads(page_content.text)
        ip_ranges = sorted({x for v in ip_ranges_json.values() for x in v})

    except requests.exceptions.RequestException:
        sys.stderr.write('[-] Failed to retrieve Cloudfront IP ranges from cloudfront - trying alternate source')

        try:
            print('[*] Retrieving Cloudfront IP ranges from {}'.format(cloudfront_backup_ip_ranges_url))
            page_content = requests.get(cloudfront_backup_ip_ranges_url, timeout=10)
            ip_ranges_json = json.loads(page_content.text)
            filtered_v4_ip_ranges = [x['ip_prefix'] for x in ip_ranges_json['prefixes'] if x['service'] == 'CLOUDFRONT']
            filtered_v6_ip_ranges = [x['ipv6_prefix'] for x in ip_ranges_json['ipv6_prefixes'] if x['service'] == 'CLOUDFRONT']
            ip_ranges = filtered_v4_ip_ranges + filtered_v6_ip_ranges
        except requests.exceptions.RequestException:
            sys.stderr.write('[-] Failed to retrieve Cloudfront IP ranges')
            print('Exiting.')
            exit(1)

    return ip_ranges

def is_cloudfront_ip(ip):
    if getattr(is_cloudfront_ip, 'cloudfront_subnets', None) is None:
        cloudfront_ip_ranges = get_cloudfront_ip_ranges()
        if sys.version_info[0] == 2:
            is_cloudfront_ip.cloudfront_subnets = [ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in cloudfront_ip_ranges]
        else:
            is_cloudfront_ip.cloudfront_subnets = [ipaddress.ip_network(ip_range) for ip_range in cloudfront_ip_ranges]

    for cloudfront_subnet in is_cloudfront_ip.cloudfront_subnets:
        if cloudfront_subnet.overlaps(ipaddress.ip_network(ip)):
            return True
    return False


def uses_cloudfront(domain):
    answers = dns.resolver.query(domain, 'A')

    for answer in answers:
        if is_cloudfront_ip(answer):
            return True

    return False
