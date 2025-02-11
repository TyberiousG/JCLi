from Interpreter.parser import JCLParser
from Interpreter.validator import JCLValidator

class JCLiInterpreter:
    def __init__(self):
        self.parser = JCLParser()
        self.validator = JCLValidator()

    def process_job(self, jcl_script):
        job = self.parser.parse(jcl_script)
        errors = self.validator.validate(job)

        if errors:
            for error in errors:
                print(f"Validation Error: {error}")
        else:
            self.display_job(job)

    def display_job(self, job):
        print(f"Job Name: {job.name}")
        print(f"Class: {job.job_class}")
        print(f"Priority: {job.priority}")
        print(f"User: {job.user}")
        print(f"Program: {job.program}")
        print(f"Arguments: {job.arguments}")
        print(f"Output: {job.output}")

if __name__ == '__main__':
    interpreter = JCLiInterpreter()
    jcl_script = """
    //JOBNAME  JOB CLASS=A,PRTY=5,USER=admin
    //STEP1    EXEC PGM=/usr/bin/python3,ARGS='script.py --arg1 value'
    //OUTFILE  DD SYSOUT=A
    """
    interpreter.process_job(jcl_script)
