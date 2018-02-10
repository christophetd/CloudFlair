import dns.resolver

def is_valid_domain(domain):
    try:
        dns.resolver.query(domain, 'A')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return False
