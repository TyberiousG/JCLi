import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from jcli.cli import main
from jcli.store import JobStore


SCRIPT = """//CLIJOB JOB CLASS=A,PRTY=2,USER=tester
//STEP1 EXEC PGM=/bin/echo,ARGS='hello cli'
//OUTPUT DD SYSOUT=A
"""


class CLITests(unittest.TestCase):
    def test_submit_status_show_job_and_hold_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            script_path = tmp_path / "job.jcli"
            script_path.write_text(SCRIPT, encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                submit_code = main(["--state-dir", str(tmp_path), "submit", str(script_path)])
            self.assertEqual(0, submit_code)
            self.assertIn("Submitted job CLIJOB", stdout.getvalue())
            self.assertEqual("", stderr.getvalue())

            status_out = io.StringIO()
            with redirect_stdout(status_out):
                status_code = main(["--state-dir", str(tmp_path), "status"])
            self.assertEqual(0, status_code)
            self.assertIn("CLIJOB", status_out.getvalue())

            store = JobStore(tmp_path / "jcli.db")
            job_id = store.get_job_by_name("CLIJOB").id

            hold_err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(hold_err):
                hold_code = main(["--state-dir", str(tmp_path), "hold", str(job_id)])
            self.assertEqual(0, hold_code)
            self.assertEqual("", hold_err.getvalue())

            show_out = io.StringIO()
            with redirect_stdout(show_out):
                show_code = main(["--state-dir", str(tmp_path), "show-job", str(job_id)])
            self.assertEqual(0, show_code)
            self.assertIn("State: HELD", show_out.getvalue())

            release_out = io.StringIO()
            with redirect_stdout(release_out):
                release_code = main(["--state-dir", str(tmp_path), "release", str(job_id)])
            self.assertEqual(0, release_code)
            self.assertIn("Released job", release_out.getvalue())


if __name__ == "__main__":
    unittest.main()
