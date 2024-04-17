check:
	python scripts/check_install.py "./.env"

uv:
	uv pip compile pyproject.toml --all-extras -o requirements.txt
	uv pip install -r requirements.txt

setup:
	pip install uv
	uv pip compile pyproject.toml --all-extras -o requirements.txt
	uv pip install -r requirements.txt 
	## Touch an .env file to receive user credentials
	touch .env