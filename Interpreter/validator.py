class JCLValidator:
    def __init__(self):
        pass

    def validate(self, job):
        errors = []

        # Validate job name
        if not job.name:
            errors.append("Job name is missing.")

        # Validate job class
        if job.job_class not in ['A', 'B', 'C', 'D', 'E', 'H']:
            errors.append(f"Invalid job class '{job.job_class}'. Must be A, B, C, D, E, or H.")

        # Validate priority
        if not isinstance(job.priority, int) or not (1 <= job.priority <= 10):
            errors.append(f"Priority '{job.priority}' is invalid. Must be between 1 and 10.")

        # Validate program path
        if job.steps:
            for step in job.steps:
                if not step.get("program"):
                    errors.append(f"Step '{step.get('name', 'UNKNOWN')}' is missing a program (PGM).")
        elif not job.program:
            errors.append("Program (PGM) is missing.")

        # Additional checks can be added here

        return errors

if __name__ == '__main__':
    from job_definition import JobDefinition

    # Sample job for testing
    job = JobDefinition(name='TESTJOB', job_class='D', priority=15, program='')
    validator = JCLValidator()
    validation_errors = validator.validate(job)

    if validation_errors:
        for error in validation_errors:
            print(f"Validation Error: {error}")
    else:
        print("Job is valid.")
