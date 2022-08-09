define setup_env
    $(eval ENV_FILE := $(1).env)
    @echo " - setup env $(ENV_FILE)"
    $(eval include $(1).env)
    $(eval export)
endef

devEnv:
	$(call setup_env, dev)

prodEnv:
	$(call setup_env, prod)

sampleEnv:
	$(call setup_env, prod)

tests:
	echo Running tests
	pytest tests/

quality_checks:
	echo Running quality checks
	isort .
	black .
	pylint --recursive=y .

prefect:
#	prefect config set PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT-ID]/workspaces/[WORKSPACE-ID]"
#	prefect config set PREFECT_API_KEY=${PREFECT_API_KEY}
	prefect cloud workspace set --workspace ${PREFECT_WORKSPACE}
	prefect cloud login -k ${PREFECT_API_KEY}

setup: prodEnv prefect
	echo Running installers
#	pipenv install --dev
#	pre-commit install

setup_dev: devEnv prefect
	echo Running installers
	pipenv install --dev
	pre-commit install

run: tests quality_checks
	echo Running All
