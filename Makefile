setup:
	## Install pipx and poetry
	pip install pipx
	pipx ensurepath
	pipx install --force poetry==1.3.1
	pipx install --force -e .
	## Touch an .env file to receive user credentials
	touch .env

check:
	python scripts/check_install.py "./.env"