#!/usr/bin/env python3

import dns_utils
import cloudflare_utils
import os
import sys
import censys_search
import requests
import urllib3
from html_similarity import similarity
import cli
import utils
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

config = {
    'http_timeout_seconds': 3,
    'response_similarity_threshold': 0.9
}


def find_hosts(domain, censys_api_id, censys_api_secret):
    if not dns_utils.is_valid_domain(domain):
        logging.critical(f'The domain "{domain}" looks invalid.')
        exit(1)

    if not cloudflare_utils.uses_cloudflare(domain):
        logging.critical(f'The domain "{domain}" does not seem to be behind CloudFlare.')
        exit(0)

    logging.info('The target appears to be behind CloudFlare.')

    logging.info('Looking for certificates matching "%s" using Censys' % domain)
    cert_fingerprints = censys_search.get_certificates(domain, censys_api_id, censys_api_secret)
    logging.info(f'{len(cert_fingerprints)} certificates matching "{domain}" found.')

    if len(cert_fingerprints) is 0:
        logging.info('Exiting.')
        exit(0)

    logging.info('Looking for IPv4 hosts presenting these certificates...')
    hosts = censys_search.get_hosts(cert_fingerprints, censys_api_id, censys_api_secret)
    hosts = cloudflare_utils.filter_cloudflare_ips(hosts)
    logging.info(f'{len(hosts)} IPv4 hosts presenting a certificate issued to "{domain}" were found.')

    if len(hosts) is 0:
        logging.info('The target is most likely not vulnerable.')
        exit(0)

    return set(hosts)


def print_hosts(hosts):
    for host in hosts:
        print('  - %s' % host)
    print('')


def retrieve_original_page(domain):
    url = 'https://' + domain
    logging.info(f'Retrieving target homepage at {url}')
    try:
        headers = {'User-Agent': utils.get_user_agent()}
        original_response = requests.get(url, timeout=config['http_timeout_seconds'], headers=headers)
    except requests.exceptions.Timeout:
        logging.critical(f'{url} timed out after {config["http_timeout_seconds"]} seconds.')
        exit(1)
    except requests.exceptions.RequestException as e:
        logging.critical('Failed to retrieve %s' % url)
        exit(1)

    status_code = original_response.status_code
    if status_code != 200:
        logging.critical(f'{url} responded with an unexpected HTTP status code {status_code}')
        exit(1)

    if original_response.url != url:
        logging.info(f'"{url}" redirected to "{original_response.url}", following redirect')

    return original_response


def print_origins(origins):
    for origin in origins:
        print('  - %s (%s)' % (origin[0], origin[1]))

    print('')


def save_origins_to_file(origins, output_file):
    if output_file is None:
        return

    try:
        with open(output_file, 'w') as f:
            for origin in origins:
                f.write(origin[0] + '\n')
        logging.info(f'Wrote {len(origins)} likely origins to output file {os.path.abspath(output_file)}')
    except IOError as e:
        logging.error(f'Unable to write to output file {output_file}: {e}')

def find_origins(domain, candidates):
    logging.info('Testing candidate origin servers')
    original_response = retrieve_original_page(domain)
    host_header_value = original_response.url.replace('https://', '').split('/')[0]
    origins = []
    for host in candidates:
        try:
            print('  - %s' % host)
            url = 'https://' + host
            headers = {
                'Host': host_header_value, # only keep the TLD, without any slashes
                'User-Agent': utils.get_user_agent()
            }
            response = requests.get(url, timeout=config['http_timeout_seconds'], headers=headers, verify=False)
        except requests.exceptions.Timeout:
            print('      timed out after %d seconds' % config['http_timeout_seconds'])
            continue
        except requests.exceptions.RequestException as e:
            print('      unable to retrieve')
            continue

        if response.status_code != 200:
            print('      responded with an unexpected HTTP status code %d' % response.status_code)
            continue

        if response.text == original_response.text:
            origins.append((host, 'HTML content identical to %s' % domain))
            continue

        if len(response.text) > 0:
            try:
                page_similarity = similarity(response.text, original_response.text)
            except:
                page_similarity = 0

            if page_similarity > config['response_similarity_threshold']:
                origins.append((host, 'HTML content is %d %% structurally similar to %s' % (round(100 *page_similarity, 2), domain)))

    return origins


def main(domain, output_file, censys_api_id, censys_api_secret):
    hosts = find_hosts(domain, censys_api_id, censys_api_secret)
    print_hosts(hosts)
    origins = find_origins(domain, hosts)

    if len(origins) is 0:
        logging.info('Did not find any origin server.')
        exit(0)

    logging.info(f'\nFound {len(origins)} likely origin servers of {domain}!')
    print_origins(origins)
    save_origins_to_file(origins, output_file)


if __name__ == "__main__":
    args = cli.parser.parse_args()

    censys_api_id = None
    censys_api_secret = None

    if 'CENSYS_API_ID' in os.environ and 'CENSYS_API_SECRET' in os.environ:
        censys_api_id = os.environ['CENSYS_API_ID']
        censys_api_secret = os.environ['CENSYS_API_SECRET']

    if args.censys_api_id and args.censys_api_secret:
        censys_api_id = args.censys_api_id
        censys_api_secret = args.censys_api_secret

    if None in [censys_api_id, censys_api_secret]:
        logging.critical('[!] Please set your Censys API ID and secret from your environment '
                         '(CENSYS_API_ID and CENSYS_API_SECRET) or from the command line.')
        exit(1)

    main(args.domain, args.output_file, censys_api_id, censys_api_secret)
