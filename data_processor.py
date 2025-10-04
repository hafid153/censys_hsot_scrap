import re
import sys
from collections import OrderedDict

def normalize_service(service):
    service = service.strip().lower()
    return service

def extract_blocks(lines):
    blocks = []
    current_block = []

    for line in lines:
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}', line):  # line starts with IP
            if current_block:
                blocks.append(current_block)
                current_block = []
        current_block.append(line)
    if current_block:
        blocks.append(current_block)

    return blocks

def parse_block(block):
    data = OrderedDict()
    block_text = " ".join(block)

    # IP & hostname
    m_ip = re.match(r'^\s*(\d{1,3}(?:\.\d{1,3}){3})(?:\s*\((.*?)\))?', block[0])
    if m_ip:
        data['ip'] = m_ip.group(1)
        hostname = m_ip.group(2)
        data['hostname'] = hostname if hostname else None
    else:
        return None  # skip invalid block

    # ASN (e.g., "UPCLOUD (202053)")
    m_asn = re.search(r'([A-Z0-9\-\. ]+)\s*\((\d{1,6})\)', block_text)
    data['asn'] = f"{m_asn.group(1).strip()} ({m_asn.group(2)})" if m_asn else None

    # Location (e.g., "Stockholm, Sweden")
    m_loc = re.search(r'([A-Za-z\-\.\' ]+,\s*[A-Za-z\-\.\' ]+)', block_text)
    data['location'] = m_loc.group(1).strip() if m_loc else None

    # Ports (look for all PORT/SERVICE patterns)
    port_matches = re.findall(r'(\d{1,5})/([A-Za-z0-9\-_\.]+)', block_text)
    ports = []
    for port, service in port_matches:
        ports.append({
            'port': int(port),
            'service': normalize_service(service)
        })

    data['ports'] = ports if ports else []
    return data

def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = extract_blocks(lines)
    hosts = []

    for block in blocks:
        entry = parse_block(block)
        if entry:
            hosts.append(entry)
    return hosts

def write_yaml(hosts, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("hosts:\n")
        for host in hosts:
            hostname = f"\"{host['hostname']}\"" if host['hostname'] else "null"
            asn = f"\"{host['asn']}\"" if host['asn'] else "null"
            location = f"\"{host['location']}\"" if host['location'] else "null"

            f.write(f"  - ip: \"{host['ip']}\"\n")
            f.write(f"    hostname: {hostname}\n")
            f.write(f"    asn: {asn}\n")
            f.write(f"    location: {location}\n")
            f.write(f"    ports:\n")
            if host['ports']:
                for p in host['ports']:
                    f.write(f"      - {{port: {p['port']}, service: \"{p['service']}\"}}\n")
            else:
                f.write("      - {}\n")


def run_data_process():
    '''
    if len(sys.argv) != 3:
        print("Usage: python3 extract_censys_yaml.py input.txt output.yml")
        sys.exit(1)
    '''
    input_file ="node_js/page_text.txt" #sys.argv[1]
    output_file ="hosts.yml" #sys.argv[2]

    hosts = parse_file(input_file)
    write_yaml(hosts, output_file)
    print(f"[✓] {len(hosts)} hosts parsed and written to {output_file}")

if __name__ == "__main__":
    run_data_process()
