.PHONY: test test-fast test-cov test-slow lint

test:
	cd backend && pytest

test-fast:
	cd backend && pytest -m "not slow"

test-cov:
	cd backend && pytest --cov=app --cov-report=term-missing --cov-report=html

test-slow:
	cd backend && pytest -m slow

lint:
	cd backend && python -m py_compile app/main.py app/core/config.py \
	    app/core/security.py app/api/auth.py app/api/resumes.py \
	    app/api/jobs.py app/api/matches.py app/api/analytics.py
