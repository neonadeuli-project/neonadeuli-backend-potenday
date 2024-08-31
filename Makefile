.PHONY: clean install lint test run all

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

install:
	pip install -r requirements.txt

lint:
	flake8 .

test:
	pytest test/

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

all: clean install lint test run