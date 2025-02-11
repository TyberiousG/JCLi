from Interpreter.job_definition import JobDefinition

class JCLParser:
    def parse(self, script):
        lines = script.strip().splitlines()
        job = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith("//") and "JOB" in line:
                job.update(self._parse_job_line(line))
            elif line.startswith("//") and "EXEC" in line:
                job.update(self._parse_exec_line(line))
            elif line.startswith("//") and "DD" in line:
                job.update(self._parse_dd_line(line))

        return JobDefinition(
            name=job.get("name", ""),
            job_class=job.get("class", "C"),
            priority=int(job.get("priority", 0)),
            user=job.get("user", "default"),
            program=job.get("program", ""),
            arguments=job.get("arguments", ""),
            output=job.get("output", "SYSOUT")
        )

    def _parse_job_line(self, line):
        parts = line.split()
        job_details = {"name": parts[0][2:]}  # Strip the leading //

        # Join the rest of the line (after JOB) and split by commas
        params = ' '.join(parts[2:]).split(',')

        for param in params:
            if '=' in param:
                key, value = param.split('=')
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
        parts = line.split()
        exec_details = {}

        for part in parts[2:]:  # Skip "//STEP1 EXEC"
            if part.startswith("PGM="):
                exec_details["program"] = part.split("=")[1]
            elif part.startswith("ARGS="):
                exec_details["arguments"] = part.split("=", 1)[1].strip("'")

        return exec_details

    def _parse_dd_line(self, line):
        parts = line.split()
        dd_details = {}

        for part in parts[2:]:  # Skip "//OUTFILE DD"
            if part.startswith("SYSOUT="):
                dd_details["output"] = part.split("=")[1]

        return dd_details
