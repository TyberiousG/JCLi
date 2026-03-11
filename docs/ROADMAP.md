# JCLi Roadmap

## Next Features

### Dependencies

- Add `AFTER=` or equivalent job-level dependency metadata
- Block dispatch until prerequisite jobs finish successfully
- Surface dependency graphs in `show-job`

### Retries

- Add retry policy fields for job and step definitions
- Capture retry counts and backoff timing in SQLite
- Distinguish terminal failure from retryable failure

### Schedules

- Add recurring submission plans for daily, hourly, and calendar-driven jobs
- Separate schedule definitions from individual job runs
- Preserve operator override semantics for hold and cancel

### REST API

- Expose submit, status, job detail, and log retrieval endpoints
- Keep the CLI as a first-class client of the same service layer
- Add authentication and structured API errors

### Remote Workers

- Introduce worker registration and lease-based job claiming
- Keep SQLite or evolve to a stronger coordination backend when multi-node scale demands it
- Preserve the JCLi control plane and job model as the stable contract
