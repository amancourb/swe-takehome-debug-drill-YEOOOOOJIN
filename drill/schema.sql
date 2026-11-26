drop table if exists job_executions;
drop table if exists job_configs;
drop table if exists jobs;

create table jobs (
    id          bigserial primary key,
    payload     text        not null,
    status      text        not null default 'pending',
    claimed_by  text,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

-- per-job execution settings, looked up by the worker after it picks a job
create table job_configs (
    job_id      bigint primary key references jobs(id),
    max_retries int  not null default 3,
    notify      bool not null default true
);

-- one row per actual execution. the invariant we care about:
-- exactly one row per job, ever.
create table job_executions (
    id          bigserial primary key,
    job_id      bigint      not null references jobs(id),
    worker      text        not null,
    executed_at timestamptz not null default now()
);

create index on jobs (status);
