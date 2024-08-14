# Warehouse

## Tooling
* `pre-commit install` - installs pre-commit hooks, list of hooks declared in .pre-commit-config.yaml

## Code testing
* `pre-commit run -av --hook-stage commit` - for run commit hooks on all files

## Migrations
* create migration `alembic revision --autogenerate -m "<message>"`
* apply migrations `alembic upgrade head`
* merge migrations `alembic merge heads`
