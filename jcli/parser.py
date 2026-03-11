from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from io import StringIO

from .models import DDStatement, JobDefinition, StepDefinition, ValidationError

JOB_RE = re.compile(r"^//(?P<name>[A-Z0-9#$@_-]+)\s+JOB\s+(?P<params>.+)$", re.IGNORECASE)
EXEC_RE = re.compile(r"^//(?P<name>[A-Z0-9#$@_-]+)\s+EXEC\s+(?P<params>.+)$", re.IGNORECASE)
DD_RE = re.compile(r"^//(?P<name>[A-Z0-9#$@_-]+)\s+DD\s+(?P<params>.+)$", re.IGNORECASE)


@dataclass(slots=True)
class ParseResult:
    job: JobDefinition | None
    errors: list[ValidationError]


def _split_params(blob: str) -> dict[str, str]:
    reader = csv.reader(StringIO(blob), delimiter=",", quotechar="'", skipinitialspace=True)
    params: dict[str, str] = {}
    for token in next(reader):
        token = token.strip()
        if not token:
            continue
        if "=" not in token:
            params[token.upper()] = ""
            continue
        key, value = token.split("=", 1)
        params[key.strip().upper()] = value.strip()
    return params


class JCLParser:
    """Parses the JOB / EXEC / DD subset used by JCLi."""

    def parse_text(self, text: str, source_path: str | None = None) -> ParseResult:
        errors: list[ValidationError] = []
        job_name: str | None = None
        job_class = "C"
        priority = 5
        user = "unknown"
        steps: list[StepDefinition] = []
        dd_statements: list[DDStatement] = []

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("//*"):
                continue

            if match := JOB_RE.match(line):
                if job_name is not None:
                    errors.append(ValidationError(line_number, "duplicate-job", "Only one JOB statement is allowed."))
                    continue
                params = _split_params(match.group("params"))
                job_name = match.group("name").upper()
                job_class = params.get("CLASS", "C").upper()
                user = params.get("USER", "unknown")
                try:
                    priority = int(params.get("PRTY", "5"))
                except ValueError:
                    errors.append(ValidationError(line_number, "invalid-priority", "PRTY must be an integer."))
                continue

            if match := EXEC_RE.match(line):
                params = _split_params(match.group("params"))
                program = params.get("PGM", "")
                if not program:
                    errors.append(ValidationError(line_number, "missing-program", "EXEC statement requires PGM=."))
                    continue
                steps.append(
                    StepDefinition(
                        name=match.group("name").upper(),
                        program=program,
                        arguments=params.get("ARGS", ""),
                    )
                )
                continue

            if match := DD_RE.match(line):
                params = _split_params(match.group("params"))
                sysout = params.get("SYSOUT")
                if not sysout:
                    errors.append(ValidationError(line_number, "missing-sysout", "DD statement requires SYSOUT=."))
                    continue
                dd = DDStatement(name=match.group("name").upper(), sysout=sysout.upper())
                if steps:
                    steps[-1].dd_statements.append(dd)
                else:
                    dd_statements.append(dd)
                continue

            errors.append(ValidationError(line_number, "unknown-statement", f"Unsupported statement: {line}"))

        if job_name is None:
            errors.append(ValidationError(1, "missing-job", "A JOB statement is required."))

        if not steps:
            errors.append(ValidationError(1, "missing-exec", "At least one EXEC step is required."))

        if errors:
            return ParseResult(job=None, errors=errors)

        job = JobDefinition(
            name=job_name or "UNKNOWN",
            job_class=job_class,
            priority=priority,
            user=user,
            steps=steps,
            dd_statements=dd_statements,
            source_path=source_path,
            raw_script=text,
        )
        validation_errors = self.validate(job)
        return ParseResult(job=job if not validation_errors else None, errors=validation_errors)

    def parse_file(self, path: str) -> ParseResult:
        with open(path, "r", encoding="utf-8") as handle:
            return self.parse_text(handle.read(), source_path=path)

    def validate(self, job: JobDefinition) -> list[ValidationError]:
        errors: list[ValidationError] = []
        valid_classes = {"A", "B", "C", "D", "E", "H"}
        if job.job_class not in valid_classes:
            errors.append(ValidationError(1, "invalid-class", f"Unsupported CLASS {job.job_class!r}."))
        if not 1 <= job.priority <= 10:
            errors.append(ValidationError(1, "invalid-priority-range", "PRTY must be between 1 and 10."))
        seen_steps: set[str] = set()
        for index, step in enumerate(job.steps, start=1):
            if step.name in seen_steps:
                errors.append(ValidationError(index + 1, "duplicate-step", f"Duplicate step name {step.name!r}."))
            seen_steps.add(step.name)
        return errors
