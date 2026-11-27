from __future__ import annotations

import threading

import pytest

from drill.db import connect, reset_schema
from drill.seed import seed
from drill.worker import Worker


@pytest.fixture(autouse=True)
def fresh_db() -> None:
    reset_schema()


def _executions() -> list[tuple[int, int]]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select job_id, count(*)
              from job_executions
             group by job_id
             order by job_id
            """
        )
        return cur.fetchall()


def test_single_worker_executes_every_job_once() -> None:
    ids = seed(20)
    worker = Worker("solo")
    try:
        worker.run_until_empty()
    finally:
        worker.close()

    counts = dict(_executions())
    assert set(counts) == set(ids)
    assert all(c == 1 for c in counts.values())


def test_concurrent_workers_execute_every_job_exactly_once() -> None:
    """BUG-4412: under load, some jobs are processed more than once."""
    ids = seed(40)

    workers = [Worker(f"w{i}") for i in range(4)]
    threads = [threading.Thread(target=w.run_until_empty) for w in workers]
    try:
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        for w in workers:
            w.close()

    counts = dict(_executions())
    duplicated = {job: c for job, c in counts.items() if c != 1}
    missing = set(ids) - set(counts)

    assert not missing, f"jobs never executed: {sorted(missing)}"
    assert not duplicated, f"jobs executed more than once: {duplicated}"


def test_job_claimed_mid_claim_by_another_worker_is_not_executed_twice() -> None:
    """Deterministic repro of BUG-4412.

    Worker A is paused between its SELECT and UPDATE (via its load_config call)
    while worker B claims and executes a job. Single-threaded, no sleeps.
    """
    seed(2)
    a, b = Worker("a"), Worker("b")
    # if a fix makes B wait on A's row lock, fail fast instead of hanging forever
    b.conn.execute("set lock_timeout = '5s'")

    real_load_config = a.load_config
    b_jobs: list[dict] = []

    def interleave(job_id: int) -> dict:
        b_job = b.claim_next_job()
        assert b_job is not None, "B found no pending job"
        b.execute(b_job)
        b_jobs.append(b_job)
        return real_load_config(job_id)

    a.load_config = interleave  # type: ignore[method-assign]
    try:
        a_job = a.claim_next_job()
        assert a_job is not None, "A found no pending job"
        a.execute(a_job)
    finally:
        a.close()
        b.close()

    assert b_jobs, "hook never ran; the interleaving was not exercised"
    counts = dict(_executions())
    duplicated = {job: c for job, c in counts.items() if c != 1}
    assert a_job["id"] != b_jobs[0]["id"], (
        f"A and B both claimed job {a_job['id']}; executions: {counts}"
    )
    assert not duplicated, f"jobs executed more than once: {duplicated}"
