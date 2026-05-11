.PHONY: test

test:
	docker compose run --rm web_test pytest --cov=. --cov-report=term-missing -q

coverage:
	docker compose run --rm web_test pytest --cov=. --cov-report=term-missing
