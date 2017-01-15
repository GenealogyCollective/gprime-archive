build: FORCE
	python3 setup.py build

clean: FORCE
	find | grep "~" | xargs --no-run-if-empty rm
	find | grep "__pycache__" | xargs --no-run-if-empty rm -rf
	rm -rf build

upload: FORCE
	sudo python3 setup.py sdist bdist_wheel upload

update-docs: FORCE
	python3 update-docs.py > docs/Schema.html

test: FORCE
	rm -rf test
	PYTHONPATH=. python3 -m gprime.app --site-dir=test --create="Test Family"
	PYTHONPATH=. python3 -m gprime.app --site-dir=test --add-user=demo --password=demo
	PYTHONPATH=. python3 -m gprime.app --site-dir=test --import-file=~/gprime/example/gramps/example.gramps

FORCE:
