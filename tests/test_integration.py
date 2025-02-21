# test_integration.py

import unittest
import tempfile
import os
import subprocess

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_main_generates_output_file(self):
        """
        Full integration test:
        1. Create a small CSV and a small flow logs file.
        2. Run "python -m flow_log_parser.main <logs> <csv> <output>"
        3. Verify the output file is created and has the correct content.
        """

        # CSV
        csv_content = """dstport,protocol,tag
443,tcp,secure_tag
25,tcp,email_tag
"""
        csv_path = os.path.join(self.temp_path, "lookup.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content)

        # Logs
        flow_logs_content = """2 111 eni-1 10.0.0.1 1.1.1.1 9999 443 6 1 50 0 0 ACCEPT OK
2 111 eni-2 10.0.0.2 1.1.1.2 1234 25 6 1 50 0 0 ACCEPT OK
2 111 eni-3 10.0.0.3 1.1.1.3 5678 3389 6 1 50 0 0 ACCEPT OK
"""
        logs_path = os.path.join(self.temp_path, "logs.txt")
        with open(logs_path, "w") as f:
            f.write(flow_logs_content)

        # Output file
        output_path = os.path.join(self.temp_path, "results.txt")

        # Now run the main program with subprocess
        cmd = [
            "python3", 
            "-m", 
            "flow_log_parser.main", 
            logs_path, 
            csv_path, 
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Expect successful exit
        self.assertEqual(result.returncode, 0, msg=f"Error running main: {result.stderr}")

        # Now let's check the output file
        with open(output_path, "r") as outf:
            output_lines = outf.read().strip().splitlines()

        # We expect Tag Counts and Port/Protocol lines
        # Let's just check that "secure_tag" and "email_tag" appear,
        # plus "Untagged" for 3389 (since it's not in CSV).
        joined_output = "\n".join(output_lines)

        self.assertIn("Tag,Count", joined_output)
        self.assertIn("secure_tag", joined_output)
        self.assertIn("email_tag", joined_output)
        self.assertIn("Untagged", joined_output)

        self.assertIn("Port,Protocol,Count", joined_output)
        self.assertIn("443,tcp", joined_output)
        self.assertIn("25,tcp", joined_output)
        self.assertIn("3389,tcp", joined_output)

if __name__ == '__main__':
    unittest.main()
