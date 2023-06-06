# CloudFlair

CloudFlair is a tool to find origin servers of websites protected by CloudFlare (or CloudFront) which are publicly exposed and don't appropriately restrict network access to the relevant CDN IP ranges.

The tool uses Internet-wide scan data from [Censys](https://censys.io) to find exposed IPv4 hosts presenting an SSL certificate associated with the target's domain name. API keys are required and can be retrieved from your [Censys account](https://search.censys.io/account/api).

For more detail about this common misconfiguration and how CloudFlair works, refer to the companion blog post at <https://blog.christophetd.fr/bypassing-cloudflare-using-internet-wide-scan-data/>.

Here's what CloudFlair looks like in action.

```bash
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

1. Register an account (free) on <https://search.censys.io/register>
2. Browse to <https://search.censys.io/account/api>, and set two environment variables with your API ID and API secret

```bash
$ export CENSYS_API_ID=...
$ export CENSYS_API_SECRET=...
```

3. Clone the repository

```bash
$ git clone https://github.com/christophetd/CloudFlair.git
```

4. Create a virtual env and install the dependencies

```bash
cd CloudFlair
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Run CloudFlair (see [Usage](#usage) below for more detail)

```bash
python cloudflair.py myvulnerable.site
```

or for CloudFront 
```bash
python cloudflair.py myvulnerable.site --cloudfront
```

## Usage

```bash
$ python cloudflair.py --help

usage: cloudflair.py [-h] [-o OUTPUT_FILE] [--censys-api-id CENSYS_API_ID] [--censys-api-secret CENSYS_API_SECRET] [--cloudfront] domain

positional arguments:
  domain                The domain to scan

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        A file to output likely origin servers to (default: None)
  --censys-api-id CENSYS_API_ID
                        Censys API ID. Can also be defined using the CENSYS_API_ID environment variable (default: None)
  --censys-api-secret CENSYS_API_SECRET
                        Censys API secret. Can also be defined using the CENSYS_API_SECRET environment variable (default: None)
  --cloudfront          Check Cloudfront instead of CloudFlare. (default: False)
```

## Docker image

A lightweight Docker image of CloudFlair ([`christophetd/cloudflair`](https://hub.docker.com/r/christophetd/cloudflair/)) is provided. A scan can easily be instantiated using the following command.

```bash
$ docker run --rm -e CENSYS_API_ID=your-id -e CENSYS_API_SECRET=your-secret christophetd/cloudflair myvulnerable.site
```

You can also create a file containing the definition of the environment variables, and use the Docker`--env-file` option.

```bash
$ cat censys.env
CENSYS_API_ID=your-id
CENSYS_API_SECRET=your-secret

$ docker run --rm --env-file=censys.env christophetd/cloudflair myvulnerable.site
```

## Compatibility

Tested on Python 3.6. Feel free to [open an issue](https://github.com/christophetd/cloudflair/issues/new) if you have bug reports or questions.
