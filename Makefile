clean:
	find | grep "~" | xargs --no-run-if-empty rm
	find | grep "__pycache__" | xargs --no-run-if-empty rm -rf
	rm -rf build

build:
	python3 setup.py build

upload:
	sudo python3 setup.py sdist bdist_wheel upload

update-docs:
	python3 update-docs.py > docs/Schema.html
