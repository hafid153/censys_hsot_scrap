import re
from collections import OrderedDict

def normalize_service(service):
    service = service.strip().lower()
    return service

def extract_blocks_from_lines(lines):
    blocks = []
    current_block = []

    for line in lines:
        
        if re.match(r'^\s*\d{1,3}(?:\.\d{1,3}){3}', line):
            if current_block:
                blocks.append(current_block)
                current_block = []
        current_block.append(line.rstrip())
    if current_block:
        blocks.append(current_block)

    return blocks

def parse_block(block):
    data = OrderedDict()
    block_text = " ".join(block)

    
    m_ip = re.match(r'^\s*(\d{1,3}(?:\.\d{1,3}){3})(?:\s*\((.*?)\))?', block[0])
    if m_ip:
        data['ip'] = m_ip.group(1)
        hostname = m_ip.group(2)
        data['hostname'] = hostname if hostname else None
    else:
        return None  

    
    m_asn = re.search(r'([A-Z0-9\-\.\s]+)\s*\((\d{1,6})\)', block_text, re.I)
    data['asn'] = f"{m_asn.group(1).strip()} ({m_asn.group(2)})" if m_asn else None

    
    m_loc = re.search(r'([A-Za-z\-\.\' ]+,\s*[A-Za-z\-\.\' ]+)', block_text)
    data['location'] = m_loc.group(1).strip() if m_loc else None

    
    port_matches = re.findall(r'(\d{1,5})/([A-Za-z0-9\-_\.]+)', block_text)
    ports = []
    for port, service in port_matches:
        try:
            ports.append({
                'port': int(port),
                'service': normalize_service(service)
            })
        except ValueError:
            continue

    data['ports'] = ports if ports else []
    return data

def parse_text(text):
    if text is None:
        return []

    lines = [l for l in text.splitlines() if l.strip() != ""]
    blocks = extract_blocks_from_lines(lines)
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

def run_data_process(data,output_file):
    
    hosts = parse_text(data)
    write_yaml(hosts, output_file)
    print(f"[✓] {len(hosts)} hosts parsed and written to {output_file}")
