# test_parser.py

import unittest
import tempfile
import os

from flow_log_parser.parser import loadLookupTable, parseFlowLogs

class TestFlowLogParser(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

    def tearDown(self):
        # Cleanup
        self.temp_dir.cleanup()

    def test_load_lookup_table_valid(self):
        """
        Test loading a valid lookup CSV with multiple rows.
        """
        csv_content = """dstport,protocol,tag
25,tcp,sv_P1
68,udp,sv_P2
110,tcp,email
"""
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content)

        lookup_dict = loadLookupTable(csv_path)
        self.assertEqual(lookup_dict.get((25, 'tcp')), "sv_P1")
        self.assertEqual(lookup_dict.get((68, 'udp')), "sv_P2")
        self.assertEqual(lookup_dict.get((110, 'tcp')), "email")

    def test_load_lookup_table_invalid_port(self):
        """
        Rows with invalid integer ports should be skipped.
        """
        csv_content = """dstport,protocol,tag
25,tcp,sv_P1
invalid_port,tcp,skip_me
80,tcp,http
"""
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content)

        lookup_dict = loadLookupTable(csv_path)
        self.assertIn((25, 'tcp'), lookup_dict)
        self.assertIn((80, 'tcp'), lookup_dict)
        self.assertNotIn(('invalid_port', 'tcp'), lookup_dict)
        self.assertEqual(len(lookup_dict), 2)

    def test_load_lookup_table_missing_columns(self):
        """
        If CSV is missing columns, those rows are skipped.
        """
        csv_content = """dstport,protocol
25,tcp
80,tcp
"""
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content)

        lookup_dict = loadLookupTable(csv_path)
        # All rows are missing 'tag' => no valid entries
        self.assertEqual(len(lookup_dict), 0)

    def test_parse_flow_logs_basic(self):
        """
        Test parse_flow_logs with a small, valid set of lines (version=2).
        """
        csv_content = """dstport,protocol,tag
443,tcp,secure
23,tcp,telnet_tag
25,tcp,email_tag
"""
        flow_logs = """2 123456 eni-zzz 10.0.0.1 1.1.1.1 1024 443 6 10 100 0 0 ACCEPT OK
2 123456 eni-zzz 10.0.0.2 1.1.1.2 9999 23 6 5 50 0 0 ACCEPT OK
2 123456 eni-zzz 10.0.0.3 1.1.1.3 1234 25 6 5 50 0 0 ACCEPT OK
"""

        # Write them to temp
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        logs_path = os.path.join(self.temp_path, "logs.txt")

        with open(csv_path, "w") as f:
            f.write(csv_content)
        with open(logs_path, "w") as f:
            f.write(flow_logs)

        lookup_dict = loadLookupTable(csv_path)
        tag_counts, portproto_counts = parseFlowLogs(logs_path, lookup_dict)

        # Check tags
        self.assertEqual(tag_counts.get("secure"), 1)
        self.assertEqual(tag_counts.get("telnet_tag"), 1)
        self.assertEqual(tag_counts.get("email_tag"), 1)
        # No untagged
        self.assertNotIn("Untagged", tag_counts)

        # Check portproto counts
        self.assertEqual(portproto_counts.get((443, "tcp")), 1)
        self.assertEqual(portproto_counts.get((23, "tcp")), 1)
        self.assertEqual(portproto_counts.get((25, "tcp")), 1)

    def test_parse_flow_logs_mixed_versions_and_invalid(self):
        """
        Some lines are version=3 or invalid -> skip. Also check 'Untagged'.
        """
        csv_content = """dstport,protocol,tag
80,tcp,http
"""
        flow_logs = """2 123456 eni-a 192.168.1.1 203.0.113.1 55 80 6 1 100 0 0 ACCEPT OK
3 123456 eni-b 192.168.1.2 203.0.113.2 80 80 6 1 100 0 0 ACCEPT OK
2 123456 eni-c 192.168.1.3 203.0.113.3 55 not_an_int 6 1 100 0 0 ACCEPT OK
2 123456 eni-d 192.168.1.4 203.0.113.4 55 9999 6 1 100 0 0 ACCEPT OK
"""
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        logs_path = os.path.join(self.temp_path, "logs.txt")
        with open(csv_path, "w") as f:
            f.write(csv_content)
        with open(logs_path, "w") as f:
            f.write(flow_logs)

        lookup_dict = loadLookupTable(csv_path)
        tag_counts, portproto_counts = parseFlowLogs(logs_path, lookup_dict)

        # 1) First line => version=2, dstport=80 => "http"
        # 2) Second line => version=3 => skipped
        # 3) Third line => "not_an_int" => skip
        # 4) Fourth line => version=2, dstport=9999 => not in CSV => "Untagged"

        self.assertEqual(tag_counts.get("http"), 1)
        self.assertEqual(tag_counts.get("Untagged"), 1)
        self.assertEqual(len(tag_counts), 2)

        self.assertEqual(portproto_counts.get((80, "tcp")), 1)
        self.assertEqual(portproto_counts.get((9999, "tcp")), 1)
        self.assertEqual(len(portproto_counts), 2)

if __name__ == '__main__':
    unittest.main()
