.PHONY: dist pypi clean

PYTHON := python

dist:
	$(PYTHON) setup.py sdist

pypi: clean
	$(PYTHON) setup.py sdist upload

clean:
	rm -rf build dist tmux_master.egg-info
