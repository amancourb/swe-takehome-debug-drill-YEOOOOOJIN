# swe-takehome-debug-drill

A short take-home exercise. **You have one week from the date in your email**, and you
can do it before or after the live interview — whichever suits your schedule.

Please budget about **30–45 minutes**. It is not a large task, and we are not looking
for polish. If it is taking substantially longer than that, stop and send us what you
have with a note about where you got stuck — that is a perfectly good submission.

**Use your normal AI tooling.** Claude Code, Copilot, Cursor, whatever you actually build
with. We are an AI-native team; using it is expected, not tolerated. We will ask to see
your session transcript.

---

## BUG-4412 — jobs are occasionally processed twice

**Reported by:** on-call
**Severity:** high

> Since we scaled the worker pool from 1 to 4 processes per host, customers have
> reported receiving duplicate notifications. `job_executions` is supposed to hold
> exactly one row per job, and it doesn't.
>
> This went unnoticed for a while because our only test ran a single worker, and it
> passes. Someone has since added a concurrent test —
> `test_concurrent_workers_execute_every_job_exactly_once` — which fails. It was
> initially marked flaky and retried in CI.

## Your task

Find it, fix it, prove it's fixed — and then tell us **why it happened**.

See [`DELIVERABLES.md`](./DELIVERABLES.md) for exactly what to send back. The written
explanation matters to us more than the patch does; please read that file before you
start so you know what we're looking for.

## Running it

```bash
docker compose up -d     # Postgres on host port 5433
make bootstrap
make test                # runs the suite
make test-loop           # runs the concurrency test 10 times
```

You should see the single-worker test pass and the concurrent one fail.

**Requirements:** Python 3.11+, Docker, Git, make. On Windows, please work in WSL2.
If you'd rather use your own Postgres, set `DATABASE_URL` and skip compose:

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

If the environment fights you, email us rather than burning your time on it — that's on
us, not you.

## Layout

| Path | What it is |
|---|---|
| `drill/worker.py` | The worker. Polls, claims, executes. |
| `drill/schema.sql` | Three tables. |
| `drill/seed.py` | Puts pending jobs on the queue. |
| `tests/test_worker.py` | The passing single-worker test and the failing concurrent one. |
