import re

from Interpreter.job_definition import JobDefinition

class JCLParser:
    def parse(self, script):
        lines = script.strip().splitlines()
        job = {"steps": []}
        
        for line in lines:
            line = line.strip()
            if line.startswith("//") and "JOB" in line:
                job.update(self._parse_job_line(line))
            elif line.startswith("//") and "EXEC" in line:
                step = self._parse_exec_line(line)
                job["steps"].append(step)
                if not job.get("program"):
                    job["program"] = step.get("program", "")
                    job["arguments"] = step.get("arguments", "")
            elif line.startswith("//") and "DD" in line:
                job.update(self._parse_dd_line(line))

        return JobDefinition(
            name=job.get("name", ""),
            job_class=job.get("class", "C"),
            priority=int(job.get("priority", 0)),
            user=job.get("user", "default"),
            program=job.get("program", ""),
            arguments=job.get("arguments", ""),
            output=job.get("output", "SYSOUT"),
            steps=job.get("steps", [])
        )

    def _parse_job_line(self, line):
        parts = line.split()
        job_details = {"name": parts[0][2:]}  # Strip the leading //
        params_blob = re.split(r"\s+JOB\s+", line, maxsplit=1)[1].strip()
        params = [part.strip() for part in params_blob.split(",") if part.strip()]

        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip().upper()
                value = value.strip()

                if key == "CLASS":
                    job_details["class"] = value
                elif key == "PRTY":
                    job_details["priority"] = value
                elif key == "USER":
                    job_details["user"] = value

        return job_details


    def _parse_exec_line(self, line):
        step_name = line[2:].split()[0]
        exec_details = {"name": step_name, "program": "", "arguments": ""}

        program_match = re.search(r"PGM=([^,\s]+)", line)
        args_match = re.search(r"ARGS='(.*)'", line)

        if program_match:
            exec_details["program"] = program_match.group(1).strip()
        if args_match:
            exec_details["arguments"] = args_match.group(1)

        return exec_details

    def _parse_dd_line(self, line):
        parts = line.split()
        dd_details = {}

        for part in parts[2:]:  # Skip "//OUTFILE DD"
            if part.startswith("SYSOUT="):
                dd_details["output"] = part.split("=")[1]

        return dd_details
