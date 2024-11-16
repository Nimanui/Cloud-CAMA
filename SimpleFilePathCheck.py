import os
import socket
import requests
import dns.resolver

# unset HTTP_PROXY
# unset HTTPS_PROXY

# Example file paths
file_paths = [
    "VehicleCreds/certificate0.pem.crt",
    "VehicleCreds/private0.pem.key",
    "VehicleData/vehicle0.csv"
]

for path in file_paths:
    if os.path.isfile(path):
        print(f"File exists: {path}")
    else:
        print(f"File not found: {path}")

try:
    ip = socket.gethostbyname("mao7934fqx392l-ats.iot.us-east-2.amazonaws.com")
    # ip = socket.gethostbyname("8.8.8.8")
    print(f"Resolved IP for endpoint: {ip}")
except Exception as e:
    print(f"Failed to resolve hostname: {e}")


try:
    response = requests.get("https://mao7934fqx392l-ats.iot.us-east-2.amazonaws.com")
    print(response.status_code)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")


resolver = dns.resolver.Resolver()
resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Use Google DNS servers
try:
    result = resolver.resolve('mao7934fqx392l-ats.iot.us-east-2.amazonaws.com')
    print("Resolved IP:", result[0].address)
except dns.exception.DNSException as e:
    print(f"DNS Resolution Error: {e}")


def resolve_dns(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')  # 'A' records are for IPv4 addresses
        for ipval in result:
            print(f"IP Address: {ipval.to_text()}")
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        print(f"DNS resolution failed: {e}")

# Resolve the AWS IoT endpoint
resolve_dns("mao7934fqx392l-ats.iot.us-east-2.amazonaws.com")