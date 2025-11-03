download_uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install:
	uv pip compile pyproject.toml --all-extras -o requirements.txt
	uv pip install -r requirements.txt
	uv pip install -e .

touch_env:
	touch .env

setup: download_uv install touch_env

check:
	python scripts/check_install.py "./.env"
