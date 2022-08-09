tests:
	echo Running tests
	pytest tests/

quality_checks:
	echo Running quality checks
	isort .
	black .
	pylint --recursive=y .

setup:
	echo Running installers
	pipenv install --dev
	pre-commit install
	echo setup

run: tests quality_checks
	echo Running All