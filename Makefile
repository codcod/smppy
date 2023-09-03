.PHONY = venv check test

export PYTHONPATH=.

venv:
	python -m venv .venv
	( bash -c "source .venv/bin/activate && python -m pip install --upgrade pip setuptools wheel"; )
	( bash -c "source .venv/bin/activate && pip install -r requirements.txt"; )
	@printf "\nDone. You can now activate the virtual environment:\n  source .venv/bin/activate\n"

check:
	mypy --strict --scripts-are-modules --implicit-reexport messaging
		#scripts/*

test:
	# pytest --cov-report html
	pytest  # configured via pyproject.toml
