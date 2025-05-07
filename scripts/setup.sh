#!/usr/bin

python -m venv venv

pip install -r requirements.txt

pip install -r requirements-dev.txt

pre-commit install
