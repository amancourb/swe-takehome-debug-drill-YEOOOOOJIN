from __future__ import annotations

import json

from drill.db import connect


def seed(n: int = 40) -> list[int]:
    """Insert n pending jobs and their configs. Returns the job ids."""
    ids: list[int] = []
    with connect() as conn, conn.cursor() as cur:
        for i in range(n):
            cur.execute(
                "insert into jobs (payload) values (%s) returning id",
                (json.dumps({"n": i, "kind": "email"}),),
            )
            job_id = cur.fetchone()[0]
            cur.execute(
                "insert into job_configs (job_id, max_retries, notify) values (%s, %s, %s)",
                (job_id, 3, i % 2 == 0),
            )
            ids.append(job_id)
        conn.commit()
    return ids


if __name__ == "__main__":  # pragma: no cover
    print(f"seeded {len(seed())} jobs")
