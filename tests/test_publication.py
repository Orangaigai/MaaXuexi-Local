"""Public export checks and invalid geometry; no user configuration or devices."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
spec = importlib.util.spec_from_file_location('publication_checks', ROOT / 'scripts/Check-Publication.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class PublicationTests(unittest.TestCase):
    def test_secrets_and_personal_paths_are_reported_without_echoing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = 'gh' + 'p_' + 'A' * 36
            (root / 'example.txt').write_text(content, 'utf-8')
            errors = checks.inspect(root, ['example.txt'])
            self.assertEqual(len(errors), 1)
            self.assertNotIn(content, str(errors))

    def test_missing_local_document_link_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[missing](missing.md)', 'utf-8')
            self.assertTrue(checks.inspect(root, ['README.md']))

    def test_local_database_is_not_a_public_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'private.sqlite3').write_bytes(b'')
            self.assertTrue(checks.inspect(root, ['private.sqlite3']))

    def test_line_endings_do_not_change_manifest_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.py'
            path.write_bytes(b'example\r\n')
            before = checks.digest(path)
            path.write_bytes(b'example\n')
            self.assertEqual(before, checks.digest(path))

    def test_invalid_click_geometry_raises_task_incomplete(self):
        from recognition_helpers import detect_click_option_boxes
        from task_support import TaskIncomplete
        with self.assertRaises(TaskIncomplete):
            detect_click_option_boxes(None)

    @unittest.skipUnless(os.name == 'nt', 'PowerShell parser')
    def test_all_powershell_entrypoints_parse(self):
        # Parse source without executing installation, services or scheduled jobs.
        command = '''$errorsFound = @(); Get-ChildItem -LiteralPath $args[0] -Filter *.ps1 | ForEach-Object {
            $tokens = $null; $parseErrors = $null
            $null = [Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$parseErrors)
            $errorsFound += $parseErrors
        }; if ($errorsFound.Count) { $errorsFound | Out-String | Write-Output; exit 1 }'''
        # Use a temporary script to preserve exact argument boundaries under PS5.
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / 'parse.ps1'
            script.write_text(command, 'utf-8')
            result = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(script),str(ROOT/'scripts')],
                                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
