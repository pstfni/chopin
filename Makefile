download_uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install:
	uv sync

touch_env:
	touch .env

setup: download_uv install touch_env

check:
	python scripts/check_install.py "./.env"
