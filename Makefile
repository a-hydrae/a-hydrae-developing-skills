.PHONY: test release-test release-test-live

test:
	python3 -m unittest discover -s tests

release-test:
	python3 scripts/release_test.py

release-test-live:
	python3 scripts/release_test.py --live
