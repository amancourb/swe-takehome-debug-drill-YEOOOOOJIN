.PHONY: bootstrap test test-loop seed clean

VENV := .venv
PY := $(VENV)/bin/python

bootstrap:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest -q

test-loop:
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		echo "--- run $$i ---"; \
		$(PY) -m pytest -q tests/test_worker.py::test_concurrent_workers_execute_every_job_exactly_once || true; \
	done

seed:
	$(PY) -m drill.seed

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__
