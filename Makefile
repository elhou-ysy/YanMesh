VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

setup: venv install

venv:
	rm -rf $(VENV)
	python3 -m venv $(VENV)

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) yanmesh.py

clean:
	rm -rf $(VENV)
	find . -name '__pycache__' -type d -exec rm -rf {} + 