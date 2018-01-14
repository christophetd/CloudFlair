# CloudFlair

CloudFlair is a tool to help find the origin servers of websites protected by CloudFlare who don't restrict network access to the CloudFlare IPs ranges.

The tool uses Internet-wide scan data from [Censys](https://censys.io) to find exposed IPv4 hosts presenting a SSL certificate associated to the target's domain name.

For more detail, refer to the companion blog post at **TODO**.

Here's what it looks like in action.

```
$ python cloudflair.py myvulnerable.site

[*] The target appears to be behind CloudFlare.
[*] Looking for certificates matching "myvulnerable.site" using Censys
[*] 75 certificates matching "myvulnerable.site" found.
[*] Looking for IPv4 hosts presenting these certificates...
[*] 10 IPv4 hosts presenting a certificate issued to "myvulnerable.site" were found.
  - 51.194.77.1
  - 223.172.21.75
  - 18.136.111.24
  - 127.200.220.231
  - 177.67.208.72
  - 137.67.239.174
  - 182.102.141.194
  - 8.154.231.164
  - 37.184.84.44
  - 78.25.205.83

[*] Retrieving target homepage at https://myvulnerable.site

[*] Testing candidate origin servers
  - 51.194.77.1
  - 223.172.21.75
  - 18.136.111.24
        responded with an unexpected HTTP status code 404
  - 127.200.220.231
        timed out after 3 seconds
  - 177.67.208.72
  - 137.67.239.174
  - 182.102.141.194
  - 8.154.231.164
  - 37.184.84.44
  - 78.25.205.83

[*] Found 2 likely origin servers of myvulnerable.site!
  - 177.67.208.72 (HTML content identical to myvulnerable.site)
  - 182.102.141.194 (HTML content identical to myvulnerable.site)
```

(_The IP addresses in this example have been obfuscated and replaced by randomly generated IPs_)

## Setup

1) Register an account (free) on https://censys.io/register
2) Browse to https://censys.io/account, and set two environment variables with your API ID and API secret

```
$ export CENSYS_API_ID=...
$ export CENSYS_API_SECRET=...
```

3) Clone the repository

```
$ git clone https://github.com/christophetd/cloudflair.git
```

4) Install the dependencies

```
$ cd cloudflair
$ pip install -r requirements.txt
```

5) Run CloudFlair (see [Usage](#Usage) below for more detail)

```
$ python cloudflair.py myvulnerable.site
```

## Usage

```
$ python cloudflair.py --help

usage: cloudflair.py [-h] [-o OUTPUT_FILE] [--censys-api-id CENSYS_API_ID]
                     [--censys-api-secret CENSYS_API_SECRET]
                     domain

positional arguments:
  domain                The domain to scan

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        A file to output likely origin servers to (default:
                        None)
  --censys-api-id CENSYS_API_ID
                        Censys API ID. Can also be defined using the
                        CENSYS_API_ID environment variable (default: None)
  --censys-api-secret CENSYS_API_SECRET
                        Censys API secret. Can also be defined using the
                        CENSYS_API_SECRET environment variable (default: None)
```

## Compatibility

Tested on Python 2.7 and 3.5. Feel free to [open an issue](https://github.com/christophetd/cloudflair/issues/new) if you have bug reports or questions.
