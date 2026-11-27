1. The code was not preventing two workers from reading the same row in the db. When multiple workers are created, they are all scheduled at once. Scheduling them all at once is okay, but there is no mechanism to lock the row a worker reads. Because of that, a worker A can pick up a pending job, loads the config, and whilst waiting on the network, another worker B can pick up that same pending job. The worker A can then set the job status to running, but by then B could have already claimed that job as well. As a result, A does write that the job was done by A and set the status to done, but this information is written over by the time B finishes.

2. We reproduced the bug before making changes. We observed that in the test using 4 workers, it failed every time, and jobs were constantly ran multiple times. Reading the code aligned with the error, since we saw that a worker would read the next job in one step but then mark it as taken in a separate step, and nothing stopped an another worker from reading that same next job. We then also reproduced the bug to happen deterministically, by forcing a worker to pause after picking up a job before it officially takes the job. When that worker is paused, another worker comes in and picks up that same job. After making the fix, the new test as well as the old test passed every time it was run.

3. There were several problems that were observed while making the fix to the worker.
	1. The database didn't do anything from stopping a job from being recorded as ran twice. The comment in the schema says that there is exactly one row per job, but there was nothing to enforce that. A possible fix is adding a uniqueness rule to job_id. This change would involve changing the database, and it should be addressed in another branch.
	2. load_config fetches stuff that nothing uses
	3. The worker.main copied the work loop instead of reusing it (can be refactored)
	4. A job's payload being invalid JSON will run the job anyway. This makes a job that is broken look like it was successful

4. Under production conditions, the issue of the database not enforcing a job being run only once and the issue of handling invalid JSON are a potential source of silent errors where something goes wrong but nothing fails/errors to indicate it



