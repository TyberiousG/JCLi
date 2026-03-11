from __future__ import annotations

import json
import logging
from pathlib import Path


class LogManager:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.system_dir = self.base_dir / "system"
        self.jobs_dir = self.base_dir / "jobs"
        self.steps_dir = self.base_dir / "steps"
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.steps_dir.mkdir(parents=True, exist_ok=True)
        logger_name = f"jcli.{self.base_dir.as_posix()}"
        self._logger = logging.getLogger(logger_name)
        if not self._logger.handlers:
            self._logger.setLevel(logging.INFO)
            self._logger.propagate = False
            system_handler = logging.FileHandler(self.system_dir / "system.log", encoding="utf-8")
            error_handler = logging.FileHandler(self.system_dir / "errors.log", encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            system_handler.setFormatter(formatter)
            error_handler.setFormatter(formatter)
            self._logger.addHandler(system_handler)
            self._logger.addHandler(error_handler)

    def system(self, message: str, *, level: int = logging.INFO, payload: dict | None = None) -> None:
        self._logger.log(level, message)
        self._append_jsonl(self.system_dir / "events.jsonl", {"level": logging.getLevelName(level), "message": message, "payload": payload or {}})

    def job_log_path(self, job_id: int, job_name: str) -> Path:
        return self.jobs_dir / f"{job_id:06d}_{job_name}.log"

    def step_log_paths(self, job_id: int, step_name: str) -> tuple[Path, Path]:
        safe_name = step_name.replace("/", "_")
        return (
            self.steps_dir / f"{job_id:06d}_{safe_name}_stdout.log",
            self.steps_dir / f"{job_id:06d}_{safe_name}_stderr.log",
        )

    def append_job_event(self, job_id: int, job_name: str, message: str, payload: dict | None = None) -> None:
        path = self.job_log_path(job_id, job_name)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{message}\n")
        self._append_jsonl(path.with_suffix(".jsonl"), {"message": message, "payload": payload or {}})

    def write_step_output(self, job_id: int, step_name: str, stdout: str, stderr: str) -> tuple[str, str]:
        stdout_path, stderr_path = self.step_log_paths(job_id, step_name)
        stdout_path.write_text(stdout, encoding="utf-8")
        stderr_path.write_text(stderr, encoding="utf-8")
        return str(stdout_path), str(stderr_path)

    def close(self) -> None:
        for handler in list(self._logger.handlers):
            handler.flush()
            handler.close()
            self._logger.removeHandler(handler)

    def _append_jsonl(self, path: Path, payload: dict) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
