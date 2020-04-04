.PHONY: test

all: test

test:
	python -m unittest discover -q tests
