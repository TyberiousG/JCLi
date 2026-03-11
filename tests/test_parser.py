import unittest

from jcli.parser import JCLParser


class ParserTests(unittest.TestCase):
    def test_parse_multistep_job(self):
        text = """
//MULTISTEP JOB CLASS=B,PRTY=4,USER=admin
//STEP1 EXEC PGM=/bin/echo,ARGS='hello'
//STEP2 EXEC PGM=/bin/echo,ARGS='world'
//OUTPUT DD SYSOUT=B
"""
        result = JCLParser().parse_text(text)
        self.assertEqual([], result.errors)
        self.assertIsNotNone(result.job)
        self.assertEqual("MULTISTEP", result.job.name)
        self.assertEqual(2, len(result.job.steps))
        self.assertEqual("OUTPUT", result.job.steps[-1].dd_statements[0].name)

    def test_parse_reports_structured_errors(self):
        text = "//STEP1 EXEC PGM=/bin/echo,ARGS='oops'"
        result = JCLParser().parse_text(text)
        self.assertTrue(result.errors)
        self.assertEqual("missing-job", result.errors[0].code)


if __name__ == "__main__":
    unittest.main()
