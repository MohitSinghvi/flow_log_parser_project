# parser.py
import csv
from .protocol_utils import protocolNumberToStr

def loadLookupTable(lookup_csv_path):
    """
    Load CSV and return a dict mapping (port_int, protocol_str_lower) -> tag (original case).
    We do case-insensitive matching on protocol only, so we store protocol in lowercase for lookups.
    """
    lookup_dict = {}
    with open(lookup_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            if 'dstport' not in row or 'protocol' not in row or 'tag' not in row:
                continue
            port_str = row['dstport'].strip().lower()
            protocol_str = row['protocol'].strip().lower()
            tag_str = row['tag'].strip()

            try:
                port_int = int(port_str)
            except ValueError:
                continue

            lookup_dict[(port_int, protocol_str)] = tag_str

    return lookup_dict

def parseFlowLogs(flow_logs_path, lookup_dict):
    """
      - Extract dstport (column 6), protocol numeric (column 7)
      - Convert protocol number to string, and classify using lookup_dict. Track the counts.
    """
    tag_counts = {}
    portproto_counts = {}

    with open(flow_logs_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty/whitespace lines

            parts = line.split()

            # We expect at least 14 columns in version 2 logs
            if len(parts) < 14:
                continue

            version = parts[0]

            # Skip any flow logs that are not version 2
            if version != '2':
                continue

            try:
                dst_port = int(parts[6])   # column 6 (dstport)
                proto_num = int(parts[7])  # column 7 (protocol)
            except ValueError:
                continue

            proto_str = protocolNumberToStr(proto_num).lower()

            # Update port/protocol combination counts
            portproto_counts[(dst_port, proto_str)] = \
                portproto_counts.get((dst_port, proto_str), 0) + 1


            tag = lookup_dict.get((dst_port, proto_str), "Untagged")

            # Update tag count
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return tag_counts, portproto_counts
