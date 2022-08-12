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
	prefect config set PREFECT_API_URL=${PREFECT_API_URL}
	prefect config set PREFECT_API_KEY=${PREFECT_API_KEY}
#	prefect cloud workspace set --workspace ${PREFECT_WORKSPACE}
#	prefect cloud login -k ${PREFECT_API_KEY}

setup_dev: devEnv
	echo Running installers
	pipenv install --dev
	pre-commit install

train_model: devEnv
	python src/training_pipeline.py

predict_model: devEnv
	python src/model_predict.py

run: tests quality_checks
	echo Running All

build-image:
	docker build -t ibombonato/mlops-showcase .

run-image:
	docker run --rm --env-file dev.env ibombonato/mlops-showcase

build: run
	pipenv lock
