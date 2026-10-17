"""Public export checks and invalid geometry; no user configuration or devices."""
import importlib.util
import os
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
spec = importlib.util.spec_from_file_location('publication_checks', ROOT / 'scripts/Check-Publication.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class PublicationTests(unittest.TestCase):
    def test_missing_schedule_record_does_not_claim_enabled(self):
        import webui
        with tempfile.TemporaryDirectory() as directory, patch.object(webui, 'Path', return_value=Path(directory)/'missing.json'):
            self.assertFalse(webui.get_schedule()['enabled'])

    def test_valid_schedule_record_preserves_actual_time_zone(self):
        import webui
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'schedule.json'
            path.write_text(json.dumps(dict(enabled=True,time='10:30',timezone='UTC',task_name='example')), 'utf-8')
            with patch.object(webui, 'Path', return_value=path):
                value = webui.get_schedule()
            self.assertTrue(value['enabled'])
            self.assertEqual((value['time'],value['timezone']),('10:30','UTC'))

    def test_invalid_schedule_record_is_disabled(self):
        import webui
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'schedule.json'
            for data in ([],dict(enabled=True,time='25:70',timezone='UTC',task_name='example')):
                path.write_text(json.dumps(data), 'utf-8')
                with patch.object(webui, 'Path', return_value=path):
                    self.assertFalse(webui.get_schedule()['enabled'])

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
