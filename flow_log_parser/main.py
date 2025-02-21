# main.py
import sys
from .parser import loadLookupTable, parseFlowLogs

def main():
    
    if len(sys.argv) < 4:
        print("Usage: python -m flow_log_parser.main <flow_logs.txt> <lookup.csv> <output_file.txt>")
        sys.exit(1)

    flow_log_file = sys.argv[1]
    lookup_csv = sys.argv[2]
    output_path = sys.argv[3]

    # 1) Here we are basically loading the lookup table
    lookup_dict = loadLookupTable(lookup_csv)

    # 2) Here we are parsing flow logs
    tag_counts, portproto_counts = parseFlowLogs(flow_log_file, lookup_dict)

    # 3) Writing results to an output file
    with open(output_path, "w", encoding="utf-8") as out_f:

        out_f.write("Tag Counts:\n")
        out_f.write("Tag,Count\n")
        for tag, count in sorted(tag_counts.items()):
            out_f.write(f"{tag},{count}\n")

        out_f.write("\n")
        out_f.write("Port/Protocol Combination Counts:\n")
        out_f.write("Port,Protocol,Count\n")
        for (port, proto), count in sorted(portproto_counts.items()):
            out_f.write(f"{port},{proto},{count}\n")

if __name__ == "__main__":
    main()
