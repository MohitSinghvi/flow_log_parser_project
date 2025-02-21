# Flow Log Parser

This project provides a Python program that parses AWS VPC Flow Logs (default format, **version 2**) and applies a **tag** based on a provided CSV lookup table (`dstport`, `protocol`, `tag`). It then generates two kinds of summary counts:

1. **Tag Counts** (including "Untagged" if no mapping is found)  
2. **(Port, Protocol) Combination Counts**  

---

## Requirements & Assumptions

1. **Version 2** default AWS flow logs only.  
2. If `(dstport, protocol)` is not in the CSV table, the line is tagged **"Untagged"**.  
3. **Case-insensitive** matching for protocol (e.g., `tcp` in CSV matches numeric protocol=6).  
4. No external libraries; only Python **standard library**.  
5. The CSV columns must be exactly `dstport`, `protocol`, `tag`.  
6. Ports must be valid integers; any row with an invalid port is skipped.  
7. Numeric protocol → string uses a minimal map: `6→tcp`, `17→udp`, `1→icmp`, `2→igmp`; unknown = `proto_<num>`.

---

## Installation

1. Install or ensure you have Python **3.x**.  
2. No extra library installs required (e.g., `pip install ...` is **not** needed).

---

## How to Run

1. **Navigate** to the project’s root folder, for example:
   
       cd flow_log_parser_project
   
2. **Execute** the main script with three arguments:
   1. **Flow logs file** (e.g., `resources/sample_flow_logs.txt`)
   2. **Lookup CSV file** (e.g., `resources/sample_lookup.csv`)
   3. **Output file** (to store the results)

   Example:
   
       python3 -m flow_log_parser.main \
           resources/sample_flow_logs.txt \
           resources/sample_lookup.csv \
           output.txt

3. After it finishes, open **`output.txt`**.

---

## How to Test

This project includes both **unit tests** and an **integration test**:

- **Unit Tests**: Validate the parser logic, CSV loading, version-check, tag assignment, etc.  
- **Integration Test**: Runs the entire script (`main.py`) in a subprocess, checking that an output file is created with expected data.

To run them all:

 cd flow_log_parser_project
 python3 -m unittest discover tests




---

## Explanation of Code Flow

- **`main.py`**:
  - Reads command-line args `(flow_logs, lookup_csv, output_file)`.
  - Calls `load_lookup_table()` to parse the CSV into a dictionary.
  - Calls `parse_flow_logs()` to process each line of the flow logs.
  - Writes two sections (“Tag Counts” and “Port/Protocol Combination Counts”) to the output file.

- **`parser.py`**:
  - `load_lookup_table()`: Reads CSV rows → `(port, protocol_lower) -> tag`.
  - `parse_flow_logs()`:
    1. Skips lines not version 2  
    2. Extracts `dstport` and `protocol` (numeric)  
    3. Converts numeric protocol to string (`protocol_utils.py`)  
    4. Checks dictionary for a match → tag or `"Untagged"`  
    5. Accumulates counts in two dictionaries (one for tags, one for port/protocol combos)

- **`test_parser.py`**:
  - Verifies correctness of CSV loading, skipping invalid rows, parsing logs, ignoring non-version-2 lines, and correct tag assignment.

- **`test_integration.py`**:
  - Runs `main.py` in a real shell subprocess to confirm the final `output.txt` has expected lines for a small sample input.


---

## Possible improvements

- For more protocol mappings (e.g., `58→icmpv6`), we can edit `protocol_utils.py`.  
- For extremely large files (GB+), streaming can be used instead of reading everything into memory.  

---
