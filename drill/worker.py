"""Background job worker.

Polls the `jobs` table for pending work, runs the job, marks it done. We run
several of these per host.
"""

from __future__ import annotations

import json
import logging
import time

import psycopg

from drill.db import DATABASE_URL

log = logging.getLogger("worker")

POLL_INTERVAL_S = 0.01


class Worker:
    def __init__(self, name: str) -> None:
        self.name = name
        self.conn = psycopg.connect(DATABASE_URL)
        self.conn.autocommit = True

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------------ claim

    def claim_next_job(self) -> dict | None:
        """Take the oldest pending job off the queue, or return None if empty."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                select id, payload
                  from jobs
                 where status = 'pending'
                 order by id
                 limit 1
                """
            )
            row = cur.fetchone()
            if row is None:
                return None

            job_id, payload = row

            # load this job's execution settings before we start
            config = self.load_config(job_id)

            cur.execute(
                """
                update jobs
                   set status = 'running',
                       claimed_by = %s,
                       updated_at = now()
                 where id = %s
                """,
                (self.name, job_id),
            )

        return {"id": job_id, "payload": payload, "config": config}

    def load_config(self, job_id: int) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(
                "select max_retries, notify from job_configs where job_id = %s",
                (job_id,),
            )
            row = cur.fetchone()
        if row is None:
            return {"max_retries": 3, "notify": True}
        return {"max_retries": row[0], "notify": row[1]}

    # ---------------------------------------------------------------- execute

    def execute(self, job: dict) -> None:
        """Do the actual work. Recorded in job_executions — exactly once per job."""
        try:
            data = json.loads(job["payload"])
        except Exception:
            data = {}

        with self.conn.cursor() as cur:
            cur.execute(
                "insert into job_executions (job_id, worker) values (%s, %s)",
                (job["id"], self.name),
            )
            cur.execute(
                "update jobs set status = 'done', updated_at = now() where id = %s",
                (job["id"],),
            )
        log.info("worker=%s job=%s executed keys=%s", self.name, job["id"], list(data))

    # ------------------------------------------------------------------- loop

    def run_until_empty(self, idle_rounds: int = 5) -> int:
        """Drain the queue. Returns how many jobs this worker executed."""
        executed = 0
        idle = 0
        while idle < idle_rounds:
            job = self.claim_next_job()
            if job is None:
                idle += 1
                time.sleep(POLL_INTERVAL_S)
                continue
            idle = 0
            self.execute(job)
            executed += 1
        return executed


def main() -> None:  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    import sys

    worker = Worker(sys.argv[1] if len(sys.argv) > 1 else "worker-1")
    try:
        while True:
            job = worker.claim_next_job()
            if job is None:
                time.sleep(0.2)
                continue
            worker.execute(job)
    finally:
        worker.close()


if __name__ == "__main__":  # pragma: no cover
    main()
